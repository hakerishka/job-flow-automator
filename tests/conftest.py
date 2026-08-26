"""
Shared Pytest Fixtures & Mocks for Job-Flow Automator Test Suite.
"""
import pytest
import pandas as pd


@pytest.fixture
def sample_raw_jobs_df():
    """Sample DataFrame mimicking raw multi-source scraped data."""
    return pd.DataFrame([
        {
            "title": "AI & Workflow Automation Specialist",
            "company": "TechInnovate GmbH",
            "location": "Berlin, Germany",
            "site": "ashby",
            "job_url": "https://jobs.ashbyhq.com/techinnovate/123",
            "date_posted": "2026-08-25",
            "description": "We are seeking an automation expert proficient with n8n, Zapier, and prompt engineering. Experience building REST API integrations is required."
        },
        {
            "title": "Robotics System Integration & Deployment Engineer",
            "company": "Amazon Operations",
            "location": "Berlin, Berlin, Germany",
            "site": "linkedin",
            "job_url": "https://www.linkedin.com/jobs/view/999888",
            "date_posted": "2026-08-24",
            "description": "Technical deployment specialist responsible for system integration, troubleshooting hardware, and authoring technical documentation."
        },
        {
            "title": "Video & Livestream Operations Specialist",
            "company": "Broadcast Pro Berlin",
            "location": "Berlin Office",
            "site": "arbeitnow",
            "job_url": "https://arbeitnow.com/view/777",
            "date_posted": "2026-08-26",
            "description": "Live production engineer experienced with vMix, OBS Studio, and NDI signal routing for webinars and virtual events."
        },
        {
            "title": "Senior Java Backend Architect",
            "company": "US Enterprise Inc",
            "location": "San Francisco, CA",
            "site": "greenhouse",
            "job_url": "https://boards.greenhouse.io/usent/jobs/111",
            "date_posted": "2026-08-25",
            "description": "Requires 10+ years of software development in Java, Kubernetes cluster management, and heavy microservices."
        }
    ])


@pytest.fixture
def mock_arbeitnow_response():
    """Sample Arbeitnow API JSON response payload."""
    return {
        "data": [
            {
                "title": "Workflow Automation Specialist",
                "company_name": "AutomationHub",
                "location": "Berlin",
                "remote": True,
                "url": "https://arbeitnow.com/jobs/automation-specialist",
                "created_at": 1724680000,
                "description": "<p>Looking for an n8n and Zapier workflow automation specialist in Berlin.</p>"
            },
            {
                "title": "Senior Java Architect",
                "company_name": "Munich Systems",
                "location": "Munich, Germany",
                "remote": False,
                "url": "https://arbeitnow.com/jobs/java-architect",
                "created_at": 1724680000,
                "description": "<p>Onsite role in Munich.</p>"
            }
        ]
    }


@pytest.fixture
def mock_greenhouse_response():
    """Sample Greenhouse API JSON response payload."""
    return {
        "jobs": [
            {
                "id": 12345,
                "title": "Technical Operations Specialist",
                "location": {"name": "Berlin, Germany"},
                "absolute_url": "https://boards.greenhouse.io/n26/jobs/12345",
                "updated_at": "2026-08-25T12:00:00Z",
                "content": "<p>Responsible for IT troubleshooting, onboarding, and SOP documentation.</p>"
            },
            {
                "id": 67890,
                "title": "Account Executive - US",
                "location": {"name": "San Francisco, California"},
                "absolute_url": "https://boards.greenhouse.io/stripe/jobs/67890",
                "updated_at": "2026-08-25T12:00:00Z",
                "content": "<p>Outbound sales quota in SF.</p>"
            }
        ]
    }


@pytest.fixture
def mock_ashby_response():
    """Sample AshbyHQ Posting API JSON response payload."""
    return {
        "jobs": [
            {
                "id": "abc-123",
                "title": "Solutions Engineer - Automation",
                "location": "Berlin Office",
                "secondaryLocations": [{"location": "London Office"}, {"location": "Remote"}],
                "isRemote": True,
                "workplaceType": "Hybrid",
                "jobUrl": "https://jobs.ashbyhq.com/n8n/abc-123",
                "publishedAt": "2026-08-25T14:00:00Z",
                "descriptionHtml": "<p>Join n8n as a Solutions Engineer building complex workflows with n8n and REST APIs.</p>"
            },
            {
                "id": "xyz-999",
                "title": "Site Reliability Engineer",
                "location": "Tokyo, Japan",
                "secondaryLocations": [],
                "isRemote": False,
                "workplaceType": "OnSite",
                "jobUrl": "https://jobs.ashbyhq.com/openai/xyz-999",
                "publishedAt": "2026-08-25T14:00:00Z",
                "descriptionHtml": "<p>Tokyo based infrastructure role.</p>"
            }
        ]
    }
