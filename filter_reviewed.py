"""
🎨 HISTORICAL REVIEW & APPLICATION FILTER
Scans ALL historical spreadsheets (.xlsx) and archive files to exclude
previously reviewed, applied, or rejected jobs from your latest scrape.

Detection mechanisms:
  1. Background Color Fill: Detects colored cells across the entire row (Excel & Google Sheets exports).
  2. Status Keywords: Checks for status words ('Applied', 'Rejected', 'Interview', 'Отклик', etc.).
  3. Master Registry: In files named 'reviewed.xlsx' / 'history.xlsx' / 'applied.xlsx', all rows are tracked.
  4. Dual-Key Matching: Deduplicates by BOTH clean URL and normalized (Title + Company) pairs.
"""

import os
import glob
import sys
import re
import pandas as pd
import openpyxl

import config


def clean_job_url(url):
    """Strip tracking parameters, query strings and trailing slashes."""
    if not url or pd.isna(url):
        return ""
    return str(url).split('?')[0].rstrip('/')


def normalize_text_for_dedup(text):
    """Normalize text for cross-platform company & title comparison."""
    if not isinstance(text, str):
        return ""
    t = text.lower()
    t = re.sub(r'\(m/f/d\)|\(m/w/d\)|\(f/m/d\)|\(all genders\)|\(gn\)', '', t)
    t = re.sub(r'\b(gmbh|inc|se|ag|ltd|corp|llc|co)\b', '', t)
    return re.sub(r'[^a-z0-9]', '', t)


def is_cell_colored(cell):
    """Detect if a cell has a non-default background color fill (works with Excel & Google Sheets exports)."""
    if not cell or not cell.fill:
        return False
    
    fill = cell.fill
    # No fill
    if fill.fill_type in [None, 'none']:
        return False
    
    # Check RGB fill
    if fill.fgColor:
        color_type = fill.fgColor.type
        if color_type == 'rgb':
            rgb = str(fill.fgColor.rgb).upper()
            # Ignore transparent or white
            if rgb not in ['00000000', 'FFFFFFFF', '00FFFFFF', 'FFFFFF', '000000']:
                return True
        elif color_type in ['theme', 'indexed']:
            # Theme colors in Google Sheets exports
            return True
            
    if fill.start_color:
        sc_type = fill.start_color.type
        if sc_type == 'rgb':
            rgb = str(fill.start_color.rgb).upper()
            if rgb not in ['00000000', 'FFFFFFFF', '00FFFFFF', 'FFFFFF', '000000']:
                return True
        elif sc_type in ['theme', 'indexed']:
            return True
            
    return False


def is_row_reviewed(row, is_registry_file=False):
    """Determine if a row in a spreadsheet has been reviewed/handled."""
    has_color = any(is_cell_colored(cell) for cell in row)
    if has_color:
        return True
    
    # Check for text status indicators in any cell of the row
    status_keywords = [kw.lower() for kw in config.REVIEWED_STATUS_KEYWORDS]
    for cell in row:
        val = str(cell.value).strip().lower() if cell.value is not None else ""
        if val in status_keywords:
            return True
            
    # If the file is specifically designated as a review registry (e.g. reviewed.xlsx)
    if is_registry_file:
        return True
        
    return False


def get_all_historical_excel_files():
    """Find all .xlsx files in project root and optional 'history/' or 'archive/' folders."""
    patterns = ['*.xlsx', 'history/*.xlsx', 'archive/*.xlsx', 'reviewed/*.xlsx']
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    return sorted(list(set(files)))


def get_latest_csv():
    """Find the most recent raw clean scrape CSV (ignoring already filtered _FILTERED.csv)."""
    candidates = glob.glob('jobs_clean_*.csv') + glob.glob('berlin_jobs_clean_*.csv')
    candidates = [f for f in candidates if not f.endswith('_FILTERED.csv')]
    
    if not candidates:
        return None
    return max(candidates, key=os.path.getctime)


def extract_historical_reviewed_keys():
    """Extract cumulative reviewed URLs and Title+Company keys from ALL historical spreadsheets."""
    excel_files = get_all_historical_excel_files()
    
    if not excel_files:
        print("⚠️ No Excel (.xlsx) files found in project directory.")
        print("💡 Place your exported Google Sheets or Excel files (e.g. 'reviewed.xlsx') here.")
        return set(), set()

    print(f"📚 Found {len(excel_files)} historical spreadsheet(s):")
    for f in excel_files:
        print(f"   • {f}")
        
    marked_urls = set()
    marked_title_company = set()

    for excel_file in excel_files:
        print(f"\n🔍 Scanning: {excel_file}...")
        is_registry = any(k in os.path.basename(excel_file).lower() for k in ['reviewed', 'applied', 'history'])
        
        try:
            wb = openpyxl.load_workbook(excel_file, data_only=True)
            sheet = wb.active

            # Find column indices
            url_col_idx = None
            title_col_idx = None
            company_col_idx = None

            for col_idx, cell in enumerate(sheet[1], 1):
                header = str(cell.value).strip().lower() if cell.value else ""
                if header == 'job_url':
                    url_col_idx = col_idx
                elif header == 'title':
                    title_col_idx = col_idx
                elif header == 'company':
                    company_col_idx = col_idx

            file_reviewed_count = 0
            for row in sheet.iter_rows(min_row=2):
                if is_row_reviewed(row, is_registry_file=is_registry):
                    url_val = row[url_col_idx - 1].value if url_col_idx else None
                    title_val = row[title_col_idx - 1].value if title_col_idx else None
                    company_val = row[company_col_idx - 1].value if company_col_idx else None

                    # Track by clean URL
                    clean_u = clean_job_url(url_val)
                    if clean_u:
                        marked_urls.add(clean_u)

                    # Track by normalized Title + Company
                    if title_val and company_val:
                        norm_t = normalize_text_for_dedup(str(title_val))
                        norm_c = normalize_text_for_dedup(str(company_val))
                        if norm_t and norm_c:
                            marked_title_company.add(f"{norm_t}_{norm_c}")

                    file_reviewed_count += 1

            print(f"   ✓ Extracted {file_reviewed_count} reviewed/processed jobs from this file.")

        except Exception as e:
            print(f"   ⚠️ Error reading '{excel_file}': {e}")

    return marked_urls, marked_title_company


def main():
    print("=" * 65)
    print("🔄 HISTORICAL REVIEW FILTER (Cumulative Multi-File Scanner)")
    print("=" * 65)

    # 1. Identify newest fresh scrape CSV
    latest_csv = get_latest_csv()
    if not latest_csv:
        print("❌ Error: No fresh scrape CSV files ('jobs_clean_*.csv') found.")
        print("💡 Run 'python main.py' first to generate a fresh jobs list.")
        sys.exit(1)
        
    print(f"\n📄 Target fresh scrape to filter: {latest_csv}")

    # 2. Extract all historical marked URLs and (Title + Company) keys
    marked_urls, marked_title_company = extract_historical_reviewed_keys()

    print("\n" + "-" * 65)
    print(f"📊 CUMULATIVE HISTORICAL DATABASE:")
    print(f"   • Unique reviewed URLs tracked: {len(marked_urls)}")
    print(f"   • Unique Title+Company pairs tracked: {len(marked_title_company)}")
    print("-" * 65)

    if not marked_urls and not marked_title_company:
        print("ℹ️ No historical reviewed entries found. Nothing to exclude.")
        return

    # 3. Read fresh scrape CSV and filter out all historical jobs
    df_new = pd.read_csv(latest_csv)
    initial_count = len(df_new)

    df_new['clean_url'] = df_new['job_url'].apply(clean_job_url)
    df_new['norm_title'] = df_new['title'].apply(normalize_text_for_dedup)
    df_new['norm_company'] = df_new['company'].apply(normalize_text_for_dedup)
    df_new['dedup_key'] = df_new['norm_title'] + "_" + df_new['norm_company']

    # Filter by URL match OR Title+Company match
    is_historical_url = df_new['clean_url'].isin(marked_urls)
    is_historical_title_company = df_new['dedup_key'].isin(marked_title_company)
    
    is_duplicate = is_historical_url | is_historical_title_company
    df_filtered = df_new[~is_duplicate].copy()
    
    final_count = len(df_filtered)
    removed_count = initial_count - final_count

    df_filtered = df_filtered.drop(columns=['clean_url', 'norm_title', 'norm_company', 'dedup_key'], errors='ignore')

    print(f"\n📈 Results:")
    print(f"   • Total jobs in latest scrape: {initial_count}")
    print(f"   • Previously reviewed/applied jobs excluded: {removed_count}")
    print(f"   • 🌟 BRAND NEW UNSEEN JOBS: {final_count}")

    # 4. Save clean filtered CSV
    base_name, ext = os.path.splitext(latest_csv)
    output_filename = f"{base_name}_FILTERED{ext}"

    df_filtered.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"\n🎉 SUCCESS! Filtered dataset saved as:\n   📁 {output_filename}")


if __name__ == "__main__":
    main()
