"""
🚀 MAIN JOB AGGREGATOR & SMART FILTER PIPELINE
Automated workflow:
  1. Multi-source scraping (LinkedIn, Indeed + VC Portfolios via custom_boards)
  2. Smart deduplication (clean URLs + normalized title/company keys)
  3. Deep LinkedIn description enrichment ('About the job')
  4. Language requirement regex filtering (drops local language constraints)
  5. Email extraction & Profile Match scoring
  6. Timestamped CSV export
"""

import sys
import os
import re
import time
import random
from datetime import datetime

# Ensure standard UTF-8 stream output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from jobspy import scrape_jobs

import config
from custom_boards import fetch_all_custom_boards


def clean_job_url(url):
    """Strip query parameters and trailing slashes from URLs for reliable deduplication."""
    return str(url).split('?')[0].rstrip('/') if pd.notna(url) else ""


def normalize_text_for_dedup(text):
    """Normalize text by removing gender markers (m/f/d), legal entities (GmbH, Inc), and special characters."""
    if not isinstance(text, str):
        return ""
    t = text.lower()
    t = re.sub(r'\(m/f/d\)|\(m/w/d\)|\(f/m/d\)|\(all genders\)|\(gn\)', '', t)
    t = re.sub(r'\b(gmbh|inc|se|ag|ltd|corp|llc|co)\b', '', t)
    return re.sub(r'[^a-z0-9]', '', t)


def is_suitable_title(title):
    """Check if title does not contain any forbidden/unwanted keywords."""
    t = str(title).lower()
    return not any(bad in t for bad in config.EXCLUDE_TITLE_KEYWORDS)


def requires_excluded_language(text):
    """Check if job description requires local language proficiency based on regex patterns."""
    text_lower = str(text).lower()
    for pattern in config.ACTIVE_LANGUAGE_PATTERNS:
        if re.search(pattern, text_lower, re.DOTALL):
            return True
    return False


def extract_emails(text):
    """Extract contact emails from job descriptions, excluding image extensions."""
    if not isinstance(text, str):
        return ""
    emails = set(re.findall(config.EMAIL_REGEX, text))
    clean_emails = [e for e in emails if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.webp'))]
    return ", ".join(clean_emails)


def calculate_match_score(row):
    """Compute 0-100% profile relevance score based on target skill keywords."""
    if not config.PROFILE_KEYWORDS:
        return 0
    text = f"{row.get('title', '')} {row.get('description', '')}".lower()
    matched_words = sum(1 for kw in config.PROFILE_KEYWORDS if kw in text)
    score = int((matched_words / len(config.PROFILE_KEYWORDS)) * 100)
    return min(score * 3, 100)


def scrape_main_boards():
    """Scrape primary platforms (LinkedIn, Indeed) via python-jobspy."""
    all_jobs_master = []
    print("\n🚀 [STAGE 1/4] SCRAPING MAIN BOARDS (LinkedIn, Indeed)...")
    print("=" * 60)
    
    total_queries = sum(len(q) for q in config.SEARCH_CATEGORIES.values())
    current_query_num = 0

    for category_name, queries in config.SEARCH_CATEGORIES.items():
        print(f"\n📂 CATEGORY: {category_name.upper()}")
        for query in queries:
            current_query_num += 1
            print(f"  [{current_query_num}/{total_queries}] 🔎 Searching: '{query}'...", end="", flush=True)
            try:
                jobs = scrape_jobs(
                    site_name=config.SEARCH_SITES,
                    search_term=query,
                    google_search_term=f"{query} jobs in {config.LOCATION}",
                    location=config.LOCATION,
                    results_wanted=config.RESULTS_PER_QUERY,
                    hours_old=config.HOURS_OLD,
                    country_indeed=config.COUNTRY_INDEED
                )
                if not jobs.empty:
                    jobs['category'] = category_name
                    jobs['search_query'] = query
                    all_jobs_master.append(jobs)
                    
                    counts = jobs['site'].str.lower().value_counts().to_dict()
                    breakdown = ", ".join([f"{site.capitalize()}: {count}" for site, count in counts.items()])
                    print(f"\n     ✓ Found: {len(jobs)} jobs ({breakdown})")
                else:
                    print(f"\n     - Found: 0 jobs")
            except Exception as e:
                print(f"\n     ⚠️ Search error on '{query}': {e}")
            
            time.sleep(random.uniform(2.0, 4.0))
            
    return pd.concat(all_jobs_master, ignore_index=True) if all_jobs_master else pd.DataFrame()


def enrich_linkedin_descriptions(df):
    """Fetch full 'About the job' text for LinkedIn postings with incomplete descriptions."""
    print("\n🔄 [STAGE 2/4] ENRICHING LINKEDIN JOB DESCRIPTIONS...")
    print("=" * 60)
    
    df['description'] = df['description'].fillna('')
    df['site'] = df['site'].fillna('')
    
    mask = (df['site'].str.lower() == 'linkedin') & (df['description'].str.len() < 500)
    linkedin_rows = df[mask]
    
    if linkedin_rows.empty:
        print("✓ All LinkedIn postings have full descriptions (or none found).")
        return df

    print(f"Enriching {len(linkedin_rows)} LinkedIn listings...")
    for index in tqdm(linkedin_rows.index, desc="Enriching LinkedIn", unit="job"):
        url = df.at[index, 'job_url']
        if pd.notna(url):
            try:
                res = requests.get(url, headers=config.REQUEST_HEADERS, timeout=8)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    desc_div = soup.find('div', class_='show-more-less-html__markup') or soup.find('section', class_='description')
                    if desc_div:
                        df.at[index, 'description'] = desc_div.get_text(separator='\n', strip=True)
                time.sleep(random.uniform(1.0, 2.0))
            except Exception:
                pass
    return df


def main():
    start_time = time.time()
    
    # 1. Scrape standard platforms
    df_raw = scrape_main_boards()
    
    # 2. Fetch alternative VC boards
    df_custom = fetch_all_custom_boards()
    if not df_custom.empty:
        df_custom['category'] = 'VC Funds & Local Boards'
        df_custom['search_query'] = 'direct_api'
        df_raw = pd.concat([df_raw, df_custom], ignore_index=True)

    if df_raw.empty:
        print("❌ No jobs retrieved. Please check connection and settings.")
        return

    raw_total = len(df_raw)

    # 3. Deduplication
    df_raw['clean_url'] = df_raw['job_url'].apply(clean_job_url)
    df_raw['norm_title'] = df_raw['title'].apply(normalize_text_for_dedup)
    df_raw['norm_company'] = df_raw['company'].apply(normalize_text_for_dedup)
    df_raw['dedup_key'] = df_raw['norm_title'] + "_" + df_raw['norm_company']

    df_dedup = df_raw.drop_duplicates(subset=['clean_url'], keep='first')
    df_dedup = df_dedup.drop_duplicates(subset=['dedup_key'], keep='first')

    # 4. Title filter
    df_filtered = df_dedup[df_dedup['title'].apply(is_suitable_title)].copy()
    df_filtered = df_filtered.drop(columns=['clean_url', 'norm_title', 'norm_company', 'dedup_key'], errors='ignore')

    print(f"\n📊 Total raw records fetched: {raw_total}")
    print(f"🎯 Unique relevant jobs after title filtering: {len(df_filtered)}")

    # 5. LinkedIn enrichment
    df_filtered = enrich_linkedin_descriptions(df_filtered)

    # 6. Language filtering, email extraction & scoring
    print("\n🧹 [STAGE 3/4] LANGUAGE FILTERING, EMAIL EXTRACTION & SCORING...")
    print("=" * 60)
    
    df_final = df_filtered[~df_filtered['description'].apply(requires_excluded_language)].copy()
    df_final['contact_email'] = df_final['description'].apply(extract_emails)
    df_final['match_score'] = df_final.apply(calculate_match_score, axis=1)
    df_final = df_final.sort_values(by='match_score', ascending=False)
    
    print(f"🎯 Total qualified matching jobs: {len(df_final)}")

    # 7. Save results
    print("\n💾 [STAGE 4/4] EXPORTING RESULTS...")
    print("=" * 60)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_filename = f"jobs_clean_{timestamp}.csv"

    existing_cols = [c for c in config.OUTPUT_COLUMNS if c in df_final.columns]
    df_final[existing_cols].to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    elapsed = round(time.time() - start_time, 1)
    print(f"🎉 Pipeline finished in {elapsed}s! Saved to: {output_filename}")
    print(f"💡 Tip: Import '{output_filename}' into Google Sheets or Excel to review!")


if __name__ == "__main__":
    main()
