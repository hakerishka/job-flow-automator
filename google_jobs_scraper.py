"""
🌐 GOOGLE JOBS CONNECTOR MODULE (Dual-Mode: Playwright Stealth & SerpApi / Proxy)
Provides automated access to Google Jobs listings with bot-protection handling:
  1. Playwright Stealth: Headless browser automation with anti-detection flags
  2. SerpApi / ValueSerp API: Optional 100% reliable free-tier API integration
  3. Graceful degradation: Continues pipeline smoothly without breaking if Google blocks
"""

import sys
import os
import time
import random
import urllib.parse
from datetime import datetime
import pandas as pd
import requests

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import config


def fetch_google_jobs_via_serpapi(queries, location, api_key, max_per_query=15):
    """Fetch Google Jobs via SerpApi (free tier supported)."""
    jobs = []
    print(f"\n🌐 [GOOGLE JOBS API] Fetching via SerpApi for {len(queries)} queries...", flush=True)
    for q in queries:
        try:
            params = {
                "engine": "google_jobs",
                "q": f"{q} {location}",
                "location": location,
                "api_key": api_key,
                "hl": "en",
                "gl": "de"
            }
            res = requests.get("https://serpapi.com/search", params=params, timeout=12)
            if res.status_code == 200:
                data = res.json()
                results = data.get("jobs_results", [])[:max_per_query]
                for r in results:
                    apply_options = r.get("apply_options", [])
                    apply_link = apply_options[0].get("link") if apply_options else r.get("share_link", "")
                    jobs.append({
                        "title": r.get("title", ""),
                        "company": r.get("company_name", ""),
                        "location": r.get("location", location),
                        "job_url": apply_link,
                        "description": r.get("description", ""),
                        "date_posted": datetime.now().strftime("%Y-%m-%d"),
                        "site": "google",
                        "search_query": q,
                        "category": "Google Jobs"
                    })
                print(f"   ✓ '{q}': {len(results)} jobs extracted.", flush=True)
            else:
                print(f"   ⚠️ SerpApi error for '{q}': HTTP {res.status_code}", flush=True)
        except Exception as e:
            print(f"   ⚠️ API query error: {e}", flush=True)
    return pd.DataFrame(jobs)


def scrape_google_jobs_playwright(queries, location="Berlin, Germany", max_per_query=15, proxy=None):
    """Scrape Google Jobs locally using Playwright Stealth with anti-detection."""
    try:
        from playwright.sync_api import sync_playwright
        from playwright_stealth.stealth import Stealth
    except ImportError:
        print("⚠️ Playwright not installed. Skipping local Google Jobs scraping.")
        return pd.DataFrame()

    all_jobs = []
    print(f"\n🌐 [GOOGLE JOBS] Launching Playwright Stealth browser for {len(queries)} queries...", flush=True)

    try:
        with sync_playwright() as p:
            launch_args = [
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-infobars',
                '--disable-dev-shm-usage'
            ]
            
            browser_kwargs = {
                "headless": True,
                "args": launch_args
            }
            if proxy:
                browser_kwargs["proxy"] = {"server": proxy}

            browser = p.chromium.launch(**browser_kwargs)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='de-DE',
                timezone_id='Europe/Berlin'
            )
            
            # Apply stealth evasions
            Stealth().apply_stealth_sync(context)
            page = context.new_page()

            for i, query in enumerate(queries, 1):
                print(f"   [{i}/{len(queries)}] 🔎 Google Jobs: '{query}'...", end="", flush=True)
                encoded_search = urllib.parse.quote_plus(f"{query} jobs in {location}")
                url = f"https://www.google.de/search?q={encoded_search}&ibp=htl;jobs#htivrt=jobs"

                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=25000)
                    time.sleep(random.uniform(1.2, 2.0))

                    # Handle cookie consent if visible
                    for sel in ['#L2AGLb', 'button:has-text("Alle akzeptieren")', 'button:has-text("Accept all")', 'button:has-text("I agree")']:
                        try:
                            btn = page.query_selector(sel)
                            if btn and btn.is_visible():
                                btn.click()
                                time.sleep(1.5)
                                break
                        except Exception:
                            pass

                    if "sorry/index" in page.url:
                        print(" - ⚠️ Google WAF challenge detected (skipped).", flush=True)
                        continue

                    # Find job card containers
                    cards = page.query_selector_all('div[data-job-id], li[data-encoded-docid], div.PwjeAc, div[role="treeitem"]')
                    if not cards:
                        cards = page.query_selector_all('li')

                    found_count = 0
                    for card in cards[:max_per_query]:
                        try:
                            card_text = card.inner_text().strip()
                            if not card_text or len(card_text) < 20:
                                continue
                            lines = [l.strip() for l in card_text.split('\n') if l.strip()]
                            title = lines[0] if len(lines) > 0 else query
                            company = lines[1] if len(lines) > 1 else "Google Employer"
                            job_loc = lines[2] if len(lines) > 2 else location

                            # Extract link
                            apply_link = f"https://www.google.de/search?q={encoded_search}&ibp=htl;jobs#htivrt=jobs&htidocid={found_count}"

                            all_jobs.append({
                                'title': title,
                                'company': company,
                                'location': job_loc,
                                'job_url': apply_link,
                                'description': card_text,
                                'date_posted': datetime.now().strftime("%Y-%m-%d"),
                                'site': 'google',
                                'search_query': query,
                                'category': 'Google Jobs'
                            })
                            found_count += 1
                        except Exception:
                            continue

                    print(f" ✓ Found: {found_count} jobs", flush=True)
                except Exception as e:
                    print(f" - ⚠️ Query notice: {e}", flush=True)

                time.sleep(random.uniform(1.5, 2.5))

            browser.close()
    except Exception as e:
        print(f"\n⚠️ Google Jobs browser error: {e}", flush=True)

    if all_jobs:
        df = pd.DataFrame(all_jobs)
        print(f"✓ Total Google Jobs extracted: {len(df)} postings.", flush=True)
        return df
    return pd.DataFrame()


def scrape_google_jobs(queries, location="Berlin, Germany", max_per_query=15, headless=True):
    """
    Unified Google Jobs entry point:
    Checks for SERPAPI_KEY first, otherwise runs local Playwright Stealth.
    """
    serpapi_key = getattr(config, 'SERPAPI_API_KEY', os.environ.get('SERPAPI_API_KEY', ''))
    if serpapi_key:
        return fetch_google_jobs_via_serpapi(queries, location, serpapi_key, max_per_query)
    
    proxy = getattr(config, 'GOOGLE_JOBS_PROXY', None)
    return scrape_google_jobs_playwright(queries, location, max_per_query, proxy=proxy)
