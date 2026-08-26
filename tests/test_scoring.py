"""
Unit Tests for Multi-Track Match Scoring Engine (evaluate_job_match).
"""
import pytest
import config


class TestMultiTrackScoringEngine:
    """Tests for config.evaluate_job_match()."""

    def test_ai_automation_track_scoring(self):
        title = "AI & Workflow Automation Specialist"
        desc = "Seeking an expert in n8n and Zapier to build automated data pipelines, prompt engineering workflows, and REST API integrations."
        res = config.evaluate_job_match(title, desc)
        
        assert res["match_score"] >= 80
        assert res["matched_track"] == "AI & Workflow Automation"
        assert "n8n" in res["matched_skills"]
        assert "Zapier" in res["matched_skills"]

    def test_tech_ops_deployment_track_scoring(self):
        title = "Technical Deployment Specialist"
        desc = "Responsible for systems integration, hardware onboarding, IT troubleshooting, and technical documentation writing."
        res = config.evaluate_job_match(title, desc)
        
        assert res["match_score"] >= 75
        assert res["matched_track"] == "Technical Operations & Deployment"
        assert "Deployment" in res["matched_skills"]
        assert "Troubleshooting" in res["matched_skills"]

    def test_media_av_livestream_track_scoring(self):
        title = "Livestream & Video Operations Engineer"
        desc = "Operate live broadcasts using vMix, OBS Studio, and NDI signal routing for corporate webinars and hybrid studio events."
        res = config.evaluate_job_match(title, desc)
        
        assert res["match_score"] >= 70
        assert res["matched_track"] == "Media, AV & Livestream Operations"
        assert "vMix" in res["matched_skills"]
        assert "OBS Studio" in res["matched_skills"]

    def test_workplace_generalist_track_scoring(self):
        title = "People Operations & Workplace Experience Coordinator"
        desc = "Coordinate workplace facilities, guest services at front desk, employee onboarding experience, and special projects."
        res = config.evaluate_job_match(title, desc)
        
        assert res["match_score"] >= 70
        assert res["matched_track"] == "Workplace & Operations Generalist"
        assert "Workplace Experience" in res["matched_skills"]

    def test_hard_requirement_penalty_applied(self):
        title = "Systems Engineer"
        desc = "Must have 10+ years of software development in C++ and Kubernetes cluster management."
        res = config.evaluate_job_match(title, desc)
        
        # Heavy dev requirements trigger penalty
        assert res["match_score"] <= 40

    def test_no_false_positive_ai_av_substring_matches(self):
        # Words like 'email', 'contain', 'have', 'travel' should NOT trigger 'ai' or 'av' tools
        title = "Office Coordinator"
        desc = "You will contain email communications and have travel arrangements organized."
        res = config.evaluate_job_match(title, desc)
        
        skills = res["matched_skills"].lower()
        assert "n8n" not in skills
        assert "vmix" not in skills
