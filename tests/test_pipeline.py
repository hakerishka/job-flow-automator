"""
Unit Tests for main.py & filter_reviewed.py helper functions.
"""
import pytest
import main
import filter_reviewed


class TestPipelineHelpers:
    """Tests for URL sanitization, text normalization, and email extraction."""

    def test_clean_job_url(self):
        raw_url = "https://www.linkedin.com/jobs/view/123456789/?trackingId=xyz&refId=abc/"
        clean = filter_reviewed.clean_job_url(raw_url)
        assert clean == "https://www.linkedin.com/jobs/view/123456789"
        assert "?" not in clean
        assert not clean.endswith("/")

    def test_normalize_text_for_dedup(self):
        title = "AI Automation Engineer (m/f/d) - Tech GmbH"
        norm = filter_reviewed.normalize_text_for_dedup(title)
        assert norm == "aiautomationengineertech"
        assert "mfd" not in norm
        assert "gmbh" not in norm

    def test_extract_emails(self):
        text = "Please send inquiries to careers@startup.io or jobs.berlin@company.de. (Ignore logo.png)"
        emails = main.extract_emails(text)
        assert "careers@startup.io" in emails
        assert "jobs.berlin@company.de" in emails
        assert "logo.png" not in emails

    def test_is_suitable_title(self):
        assert main.is_suitable_title("AI Operations Specialist") is True
        assert main.is_suitable_title("Senior Fullstack Developer") is False
        assert main.is_suitable_title("Working Student (Werkstudent)") is False
