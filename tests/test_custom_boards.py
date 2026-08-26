"""
Unit Tests for custom_boards.py with mocked network responses.
"""
from unittest.mock import patch, MagicMock
import custom_boards


class TestCustomBoardsConnectors:
    """Tests for Ashby, Greenhouse, Arbeitnow, and BSJ RSS API connectors."""

    @patch("requests.get")
    def test_get_arbeitnow_jobs(self, mock_get, mock_arbeitnow_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_arbeitnow_response
        mock_get.return_value = mock_resp

        jobs = custom_boards.get_arbeitnow_jobs()
        assert len(jobs) == 1
        assert jobs[0]["title"] == "Workflow Automation Specialist"
        assert jobs[0]["site"] == "arbeitnow"
        assert "Berlin" in jobs[0]["location"]

    @patch("requests.get")
    def test_get_greenhouse_vc_jobs(self, mock_get, mock_greenhouse_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_greenhouse_response
        mock_get.return_value = mock_resp

        test_boards = [("N26 (Berlin)", "n26")]
        jobs = custom_boards.get_greenhouse_vc_jobs(boards=test_boards)
        # Only Berlin role should be accepted; San Francisco should be dropped
        assert len(jobs) >= 1
        berlin_jobs = [j for j in jobs if "Berlin" in j["location"]]
        assert len(berlin_jobs) == len(jobs)

    @patch("requests.get")
    def test_get_ashby_vc_jobs(self, mock_get, mock_ashby_response):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_ashby_response
        mock_get.return_value = mock_resp

        test_boards = [("n8n (Berlin / Remote)", "n8n")]
        jobs = custom_boards.get_ashby_vc_jobs(boards=test_boards)
        # Berlin Office role accepted; Tokyo role dropped
        assert len(jobs) >= 1
        assert "Berlin" in jobs[0]["location"]

    @patch("requests.get")
    def test_get_bsj_rss_jobs(self, mock_get):
        rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>Operations Specialist at CoolStartup</title>
                    <link>https://berlinstartupjobs.com/ops-coolstartup/</link>
                    <pubDate>Tue, 25 Aug 2026 12:00:00 +0000</pubDate>
                    <description><![CDATA[Join our Berlin startup operations team.]]></description>
                </item>
            </channel>
        </rss>
        """
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = rss_xml.encode("utf-8")
        mock_get.return_value = mock_resp

        jobs = custom_boards.get_bsj_rss_jobs()
        assert len(jobs) == 1
        assert "Operations Specialist" in jobs[0]["title"]
        assert jobs[0]["site"] == "berlinstartupjobs"
