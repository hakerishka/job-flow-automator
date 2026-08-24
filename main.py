"""
🚀 MAIN JOB AGGREGATOR & SMART FILTER PIPELINE (High-Performance & Live Streaming)
Automated workflow:
  1. Multi-source scraping (LinkedIn, Indeed + VC Portfolios via custom_boards)
  2. Instant on-the-fly deduplication against ALL historical reviewed files (< 1ms)
  3. Fast multithreaded LinkedIn description enrichment (5x speedup via ThreadPoolExecutor)
  4. Language requirement regex filtering (drops local language constraints)
  5. Email extraction & Profile Match scoring
  6. Live stream updating (jobs_live_stream.csv) + final timestamped CSV export
"""

import sys
import os
import re
import time
import random
import glob
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure standard UTF-8 stream output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import pandas as pd
import openpyxl
import requests
from bs4 import BeautifulSoup
from jobspy import scrape_jobs

import config
from custom_boards import fetch_all_custom_boards
from google_jobs_scraper import scrape_google_jobs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIVE_STREAM_PATH = os.path.join(BASE_DIR, "jobs_live_stream.csv")


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


def load_all_historical_reviewed_keys():
    """Load all marked URLs and (Title+Company) keys from all local and historical spreadsheets."""
    marked_urls = set()
    marked_title_company = set()
    
    xlsx_files = glob.glob(os.path.join(BASE_DIR, "*.xlsx")) + glob.glob(os.path.join(BASE_DIR, "history", "*.xlsx"))
    
    for f in set(xlsx_files):
        try:
            wb = openpyxl.load_workbook(f, data_only=True)
            ws = wb.active
            url_col = None
            title_col = None
            comp_col = None
            for idx, cell in enumerate(ws[1], 1):
                h = str(cell.value).strip().lower() if cell.value else ""
                if h == 'job_url': url_col = idx
                elif h == 'title': title_col = idx
                elif h == 'company': comp_col = idx

            for row in ws.iter_rows(min_row=2, values_only=True):
                if row:
                    u = clean_job_url(row[url_col - 1]) if url_col and len(row) >= url_col else ""
                    if u: marked_urls.add(u)
                    
                    t = str(row[title_col - 1]) if title_col and len(row) >= title_col and row[title_col - 1] else ""
                    c = str(row[comp_col - 1]) if comp_col and len(row) >= comp_col and row[comp_col - 1] else ""
                    if t and c:
                        norm_k = f"{normalize_text_for_dedup(t)}_{normalize_text_for_dedup(c)}"
                        if norm_k != "_": marked_title_company.add(norm_k)
        except Exception:
            pass
            
    return marked_urls, marked_title_company


def fetch_single_linkedin_desc(url):
    """Fetch full 'About the job' text for a single LinkedIn listing."""
    if not url or pd.isna(url):
        return ""
    try:
        res = requests.get(url, headers=config.REQUEST_HEADERS, timeout=8)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            desc_div = soup.find('div', class_='show-more-less-html__markup') or soup.find('section', class_='description')
            if desc_div:
                return desc_div.get_text(separator='\n', strip=True)
    except Exception:
        pass
    return ""


def enrich_descriptions_multithreaded(df):
    """Fast concurrent enrichment of LinkedIn descriptions via ThreadPoolExecutor."""
    df['description'] = df['description'].fillna('')
    df['site'] = df['site'].fillna('')
    
    mask = (df['site'].str.lower() == 'linkedin') & (df['description'].str.len() < 500)
    linkedin_indices = list(df[mask].index)
    
    if not linkedin_indices:
        return df

    print(f"\n🔄 [FAST-ENRICH] Concurrently fetching {len(linkedin_indices)} LinkedIn descriptions (5 threads)...", flush=True)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_idx = {executor.submit(fetch_single_linkedin_desc, df.at[i, 'job_url']): i for i in linkedin_indices}
        completed_count = 0
        for future in as_completed(future_to_idx):
            i = future_to_idx[future]
            try:
                desc = future.result()
                if desc:
                    df.at[i, 'description'] = desc
            except Exception:
                pass
            completed_count += 1
            if completed_count % 10 == 0 or completed_count == len(linkedin_indices):
                print(f"   • Enriched {completed_count}/{len(linkedin_indices)} listings...", flush=True)
                
    return df


def update_live_stream_file(df_accumulated):
    """Write current deduplicated and processed jobs to jobs_live_stream.csv."""
    if df_accumulated.empty:
        return
    existing_cols = [c for c in config.OUTPUT_COLUMNS if c in df_accumulated.columns]
    df_accumulated[existing_cols].to_csv(LIVE_STREAM_PATH, index=False, encoding='utf-8-sig')


def main():
    start_time = time.time()
    print("=" * 65)
    print("🚀 JOB-FLOW AUTOMATOR — HIGH-PERFORMANCE LIVE PIPELINE")
    print("=" * 65, flush=True)

    # 1. Load historical exclusion sets (microsecond matching)
    hist_urls, hist_title_comp = load_all_historical_reviewed_keys()
    print(f"📚 Loaded {len(hist_urls)} historical URLs and {len(hist_title_comp)} (Title+Company) reviewed keys.")
    print("-" * 65, flush=True)

    all_jobs_master = []
    accumulated_live_df = pd.DataFrame()

    # 2. Fetch alternative VC boards first (super fast direct APIs ~2-3 sec)
    print("\n⚡ [STAGE 1/3] FETCHING FAST VC PORTFOLIOS (Ashby, Greenhouse, Arbeitnow)...", flush=True)
    df_custom = fetch_all_custom_boards()
    if not df_custom.empty:
        df_custom['category'] = 'VC Funds & Local Boards'
        df_custom['search_query'] = 'direct_api'
        all_jobs_master.append(df_custom)

        # Process and write first live batch
        df_custom['clean_url'] = df_custom['job_url'].apply(clean_job_url)
        df_custom['norm_title'] = df_custom['title'].apply(normalize_text_for_dedup)
        df_custom['norm_comp'] = df_custom['company'].apply(normalize_text_for_dedup)
        df_custom['dedup_key'] = df_custom['norm_title'] + "_" + df_custom['norm_comp']

        valid_custom = df_custom[
            (~df_custom['clean_url'].isin(hist_urls)) &
            (~df_custom['dedup_key'].isin(hist_title_comp)) &
            (df_custom['title'].apply(is_suitable_title)) &
            (~df_custom['description'].apply(requires_excluded_language))
        ].copy()

        if not valid_custom.empty:
            valid_custom['contact_email'] = valid_custom['description'].apply(extract_emails)
            valid_custom['match_score'] = valid_custom.apply(calculate_match_score, axis=1)
            accumulated_live_df = valid_custom.sort_values(by='match_score', ascending=False)
            update_live_stream_file(accumulated_live_df)
            print(f"🟢 [LIVE STREAM READY] {len(accumulated_live_df)} instant jobs published to Live Feed!", flush=True)

    # 3. Scrape Main Job Boards with incremental stream updates
    print("\n🔍 [STAGE 2/3] SCRAPING MAIN BOARDS (LinkedIn, Indeed)...", flush=True)
    total_queries = sum(len(q) for q in config.SEARCH_CATEGORIES.values())
    current_query_num = 0

    for category_name, queries in config.SEARCH_CATEGORIES.items():
        print(f"\n📂 CATEGORY: {category_name.upper()}", flush=True)
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
                    print(f"\n     ✓ Found: {len(jobs)} jobs ({breakdown})", flush=True)
                else:
                    print(f"\n     - Found: 0 jobs", flush=True)
            except Exception as e:
                print(f"\n     ⚠️ Error fetching '{query}': {e}", flush=True)
            
            time.sleep(random.uniform(1.5, 3.0))

    # 4. Optional Google Jobs Scraping (Playwright Stealth)
    if getattr(config, 'ENABLE_GOOGLE_JOBS', False):
        google_queries = getattr(config, 'GOOGLE_JOBS_FOCUS_QUERIES', ["AI Operations", "Product Operations"])
        max_google = getattr(config, 'GOOGLE_JOBS_MAX_PER_QUERY', 15)
        df_google = scrape_google_jobs(google_queries, location=config.LOCATION, max_per_query=max_google, headless=True)
        if not df_google.empty:
            df_google['category'] = 'Google Jobs'
            all_jobs_master.append(df_google)

    if not all_jobs_master:
        print("❌ No jobs found. Exiting.", flush=True)
        return

    # 5. Final Aggregation & Multithreaded Enrichment
    print("\n🧹 [STAGE 3/3] DEDUPLICATION, FAST ENRICHMENT & FINAL SCORING...", flush=True)
    df_raw = pd.concat(all_jobs_master, ignore_index=True)
    raw_total = len(df_raw)

    df_raw['clean_url'] = df_raw['job_url'].apply(clean_job_url)
    df_raw['norm_title'] = df_raw['title'].apply(normalize_text_for_dedup)
    df_raw['norm_company'] = df_raw['company'].apply(normalize_text_for_dedup)
    df_raw['dedup_key'] = df_raw['norm_title'] + "_" + df_raw['norm_company']

    # Cross-site and in-batch deduplication
    df_dedup = df_raw.drop_duplicates(subset=['clean_url'], keep='first')
    df_dedup = df_dedup.drop_duplicates(subset=['dedup_key'], keep='first')

    # Instant historical filter + Title filter
    df_filtered = df_dedup[
        (~df_dedup['clean_url'].isin(hist_urls)) &
        (~df_dedup['dedup_key'].isin(hist_title_comp)) &
        (df_dedup['title'].apply(is_suitable_title))
    ].copy()

    # Fast 5-thread LinkedIn enrichment
    df_filtered = enrich_descriptions_multithreaded(df_filtered)

    # Language regex filter, emails & scoring
    df_final = df_filtered[~df_filtered['description'].apply(requires_excluded_language)].copy()
    df_final['contact_email'] = df_final['description'].apply(extract_emails)
    df_final['match_score'] = df_final.apply(calculate_match_score, axis=1)
    df_final = df_final.sort_values(by='match_score', ascending=False)

    print(f"\n📊 Summary:")
    print(f"   • Total raw postings fetched: {raw_total}")
    print(f"   • Previously reviewed / duplicates excluded: {raw_total - len(df_final)}")
    print(f"   • 🌟 BRAND NEW QUALIFIED JOBS: {len(df_final)}")

    # 5. Export Final Timestamped CSV & Live Stream
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    output_filename = f"jobs_clean_{timestamp}.csv"
    output_path = os.path.join(BASE_DIR, output_filename)

    existing_cols = [c for c in config.OUTPUT_COLUMNS if c in df_final.columns]
    df_final[existing_cols].to_csv(output_path, index=False, encoding='utf-8-sig')
    df_final[existing_cols].to_csv(LIVE_STREAM_PATH, index=False, encoding='utf-8-sig')

    elapsed = round(time.time() - start_time, 1)
    print(f"\n🎉 DONE in {elapsed}s! Saved as:\n   📁 {output_filename}", flush=True)


if __name__ == "__main__":
    main()
