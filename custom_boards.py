"""
🔌 CUSTOM BOARDS MODULE (VC Portfolios, Scaleups & Tech Ecosystems)
Direct, unblocked, and official API connectors:
- AshbyHQ Posting API: n8n, ElevenLabs, PostHog, Linear, Sentry, Perplexity, Langfuse, Modal, OpenAI
- Greenhouse Public Boards API: Cherry Ventures, N26, Celonis, Contentful, Trade Republic, Figma, Stripe
- Arbeitnow API: Germany & Remote tech jobs
- Berlin Startup Jobs RSS: Real-time Berlin startup postings
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
                location = str(job.get('location', '')).strip()
                title = str(job.get('title', '')).strip()
                is_rem = job.get('remote', False)
                
                if config.is_valid_location(location, title_str=title, is_remote=is_rem):
                    soup = BeautifulSoup(job.get('description', ''), "html.parser")
                    desc = soup.get_text(separator='\n', strip=True)
                    
                    jobs_list.append({
                        'title': title,
                        'company': job.get('company_name'),
                        'location': location or ('Remote (Germany)' if is_rem else 'Berlin, Germany'),
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


GREENHOUSE_BOARDS = [
    ('Cherry Ventures', 'cherryventures'),
    ('N26 (Berlin)', 'n26'),
    ('Celonis (Munich/Remote)', 'celonis'),
    ('Contentful (Berlin)', 'contentful'),
    ('Trade Republic', 'traderepublic'),
    ('Figma', 'figma'),
    ('Stripe', 'stripe')
]

ASHBY_BOARDS = [
    ('n8n (Berlin / Remote)', 'n8n'),
    ('ElevenLabs', 'elevenlabs'),
    ('PostHog', 'posthog'),
    ('Linear', 'linear'),
    ('Sentry', 'sentry'),
    ('Perplexity AI', 'perplexity'),
    ('Langfuse (Berlin)', 'langfuse'),
    ('Modal Labs', 'modal'),
    ('OpenAI', 'openai')
]


def get_greenhouse_vc_jobs(boards=None):
    """Fetch jobs from Greenhouse public APIs (VC Portfolios & European Tech Scaleups)."""
    if boards is None:
        boards = GREENHOUSE_BOARDS
    
    jobs_list = []
    for company_name, board_slug in boards:
        try:
            res = requests.get(f"https://boards-api.greenhouse.io/v1/boards/{board_slug}/jobs?content=true", timeout=8)
            if res.status_code == 200:
                data = res.json().get('jobs', [])
                for job in data:
                    location_name = str(job.get('location', {}).get('name', '')).strip()
                    title = str(job.get('title', '')).strip()
                    
                    if config.is_valid_location(location_name, title_str=title):
                        soup = BeautifulSoup(job.get('content', ''), "html.parser")
                        desc = soup.get_text(separator='\n', strip=True)
                        
                        jobs_list.append({
                            'title': title,
                            'company': company_name,
                            'location': location_name or 'Berlin, Germany',
                            'site': 'greenhouse',
                            'job_url': job.get('absolute_url'),
                            'date_posted': job.get('updated_at'),
                            'description': desc
                        })
        except Exception as e:
            print(f"     ⚠️ Error fetching Greenhouse ({company_name}): {e}")
            
    print(f"  -> [API] Greenhouse connectors fetched: {len(jobs_list)} candidate roles.")
    return jobs_list


def get_ashby_vc_jobs(boards=None):
    """Fetch jobs from AshbyHQ public Posting APIs (AI Leaders & European Scaleups)."""
    if boards is None:
        boards = ASHBY_BOARDS
    
    jobs_list = []
    for company_name, board_slug in boards:
        try:
            url = f"https://api.ashbyhq.com/posting-api/job-board/{board_slug}"
            res = requests.get(url, headers=config.REQUEST_HEADERS, timeout=8)
            if res.status_code == 200:
                postings = res.json().get('jobs', [])
                for job in postings:
                    title = str(job.get('title', '')).strip()
                    location = str(job.get('location', '')).strip()
                    is_remote = job.get('isRemote', False)
                    workplace_type = str(job.get('workplaceType', '')).strip()
                    
                    # Combine main location with secondary locations
                    sec_locs = [str(l.get('location', '')) for l in job.get('secondaryLocations', []) if isinstance(l, dict)]
                    all_locs_str = " | ".join([location] + sec_locs) if sec_locs else location
                    
                    if config.is_valid_location(all_locs_str, title_str=title, workplace_type=workplace_type, is_remote=is_remote):
                        desc_html = job.get('descriptionHtml', '') or job.get('descriptionPlain', '')
                        soup = BeautifulSoup(desc_html, "html.parser")
                        desc = soup.get_text(separator='\n', strip=True)

                        jobs_list.append({
                            'title': title,
                            'company': company_name,
                            'location': all_locs_str or 'Berlin / Remote',
                            'site': 'ashby',
                            'job_url': job.get('jobUrl') or job.get('applyUrl'),
                            'date_posted': job.get('publishedAt'),
                            'description': desc
                        })
        except Exception as e:
            print(f"     ⚠️ Error fetching Ashby ({company_name}): {e}")
            
    print(f"  -> [API] AshbyHQ connectors fetched: {len(jobs_list)} candidate roles.")
    return jobs_list


def fetch_all_custom_boards():
    """Aggregate jobs from all custom VC & Scaleup direct connectors."""
    print("\n🌐 [CONNECTOR] FETCHING FROM VC PORTFOLIOS & SCALEUP PLATFORMS...", flush=True)
    all_custom = []
    
    # 1. Arbeitnow API
    arbeitnow = get_arbeitnow_jobs()
    if arbeitnow:
        all_custom.extend(arbeitnow)
        
    # 2. Berlin Startup Jobs RSS
    bsj = get_bsj_rss_jobs()
    if bsj:
        all_custom.extend(bsj)
        
    # 3. Greenhouse VC & Scaleups
    gh = get_greenhouse_vc_jobs()
    if gh:
        all_custom.extend(gh)
        
    # 4. AshbyHQ AI & Scaleups
    ashby = get_ashby_vc_jobs()
    if ashby:
        all_custom.extend(ashby)
        
    print(f"✓ Total Direct VC/Scaleup jobs fetched: {len(all_custom)} roles.", flush=True)
    return pd.DataFrame(all_custom) if all_custom else pd.DataFrame()
