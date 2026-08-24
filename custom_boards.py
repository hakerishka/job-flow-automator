"""
🔌 CUSTOM BOARDS MODULE
Fast direct connectors for VC portfolio job boards and niche platforms:
- Arbeitnow API (Direct tech/English roles in Germany/EU)
- Berlin Startup Jobs (RSS Feed)
- Greenhouse API (Cherry Ventures Portfolio)
- AshbyHQ GraphQL API (Earlybird VC, Atlantic Labs, HV Capital, Point Nine, Planet A)
"""

import sys
import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import config

def get_arbeitnow_jobs():
    """Fetch jobs from Arbeitnow public API."""
    jobs_list = []
    print("  -> [API] Fetching from Arbeitnow...")
    try:
        res = requests.get("https://arbeitnow.com/api/job-board-api", headers=config.REQUEST_HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json().get('data', [])
            for job in data:
                location = str(job.get('location', '')).lower()
                # Filter for target city or remote
                if 'berlin' in location or 'remote' in location or 'germany' in location:
                    soup = BeautifulSoup(job.get('description', ''), "html.parser")
                    desc = soup.get_text(separator='\n', strip=True)
                    
                    jobs_list.append({
                        'title': job.get('title'),
                        'company': job.get('company_name'),
                        'location': job.get('location'),
                        'site': 'arbeitnow',
                        'job_url': job.get('url'),
                        'date_posted': job.get('created_at'),
                        'description': desc
                    })
    except Exception as e:
        print(f"     ⚠️ Error fetching Arbeitnow: {e}")
    return jobs_list


def get_bsj_rss_jobs():
    """Fetch recent postings from Berlin Startup Jobs RSS feed."""
    jobs_list = []
    print("  -> [RSS] Fetching from Berlin Startup Jobs...")
    try:
        res = requests.get("https://berlinstartupjobs.com/feed/", headers=config.REQUEST_HEADERS, timeout=10)
        if res.status_code == 200:
            root = ET.fromstring(res.content)
            for item in root.findall('.//item'):
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                desc_raw = item.find('description').text if item.find('description') is not None else ''
                
                soup = BeautifulSoup(desc_raw, "html.parser")
                desc = soup.get_text(separator='\n', strip=True)
                
                jobs_list.append({
                    'title': title,
                    'company': 'Berlin Startup',
                    'location': 'Berlin, Germany',
                    'site': 'berlinstartupjobs',
                    'job_url': link,
                    'date_posted': pub_date,
                    'description': desc
                })
    except Exception as e:
        print(f"     ⚠️ Error fetching Berlin Startup Jobs: {e}")
    return jobs_list


def get_greenhouse_vc_jobs():
    """Fetch jobs from Greenhouse public board API (Cherry Ventures Portfolio)."""
    jobs_list = []
    print("  -> [API] Fetching from Cherry Ventures (Greenhouse)...")
    try:
        res = requests.get("https://boards-api.greenhouse.io/v1/boards/cherryventures/jobs?content=true", timeout=10)
        if res.status_code == 200:
            data = res.json().get('jobs', [])
            for job in data:
                location = str(job.get('location', {}).get('name', '')).lower()
                if 'berlin' in location or 'remote' in location or location == '' or 'germany' in location:
                    soup = BeautifulSoup(job.get('content', ''), "html.parser")
                    desc = soup.get_text(separator='\n', strip=True)
                    
                    jobs_list.append({
                        'title': job.get('title'),
                        'company': 'Cherry VC Portfolio',
                        'location': job.get('location', {}).get('name', 'Berlin'),
                        'site': 'greenhouse_vc',
                        'job_url': job.get('absolute_url'),
                        'date_posted': job.get('updated_at'),
                        'description': desc
                    })
    except Exception as e:
        print(f"     ⚠️ Error fetching Greenhouse (Cherry Ventures): {e}")
    return jobs_list


def get_ashby_vc_jobs():
    """Fetch jobs from top VC portfolios hosted on AshbyHQ GraphQL API."""
    boards = [
        ('Earlybird VC', 'earlybird'),
        ('Atlantic Labs', 'atlanticlabsfoodlabsplatform'),
        ('HV Capital', 'hvcapital'),
        ('Point Nine', 'pointnine'),
        ('Planet A', 'planeta')
    ]
    
    jobs_list = []
    url = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"
    
    for vc_name, board_name in boards:
        print(f"  -> [API] Fetching from {vc_name} (Ashby)...")
        try:
            payload = {
                "operationName": "ApiJobBoardWithTeams",
                "variables": {"organizationHostedJobsPageName": board_name},
                "query": "query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) { jobBoard: jobBoardWithTeams(organizationHostedJobsPageName: $organizationHostedJobsPageName) { jobPostings { title locationName jobUrl updatedAt } } }"
            }
            res = requests.post(url, json=payload, headers=config.REQUEST_HEADERS, timeout=10)
            if res.status_code == 200:
                postings = res.json().get('data', {}).get('jobBoard', {}).get('jobPostings', [])
                for job in postings:
                    location = str(job.get('locationName', '')).lower()
                    if 'berlin' in location or 'remote' in location or 'germany' in location:
                        jobs_list.append({
                            'title': job.get('title'),
                            'company': f'{vc_name} Portfolio',
                            'location': job.get('locationName'),
                            'site': 'ashby_vc',
                            'job_url': job.get('jobUrl'),
                            'date_posted': job.get('updatedAt'),
                            'description': ''
                        })
            time.sleep(0.5)
        except Exception as e:
            print(f"     ⚠️ Error fetching Ashby ({vc_name}): {e}")
            
    return jobs_list


def fetch_all_custom_boards():
    """Aggregate jobs from all custom non-JobSpy sources."""
    print("\n🌐 [CONNECTOR] FETCHING FROM VC PORTFOLIOS & NICHE PLATFORMS...")
    all_jobs = []
    all_jobs.extend(get_arbeitnow_jobs())
    all_jobs.extend(get_bsj_rss_jobs())
    all_jobs.extend(get_greenhouse_vc_jobs())
    all_jobs.extend(get_ashby_vc_jobs())
    
    df = pd.DataFrame(all_jobs)
    if not df.empty:
        print(f"✅ Alternative sources yielded: {len(df)} total jobs!")
    return df
