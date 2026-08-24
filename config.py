"""
⚙️ CONFIGURATION FILE
Central settings for job search, filtering, language exclusion, scoring, and review tracking.
Easily adapt this pipeline for any location, language, or job domain.
"""

# ==============================================================================
# 1. SEARCH PARAMETERS & LOCATION
# ==============================================================================
# Main location for scrapers (e.g. "Berlin, Germany", "Madrid, Spain", "London, UK", "Remote")
LOCATION = "Berlin, Germany"

# Indeed country domain (e.g. "germany", "spain", "uk", "usa", "france")
COUNTRY_INDEED = "germany"

# Scrape platforms for JobSpy ('linkedin', 'indeed', 'glassdoor', 'zip_recruiter')
SEARCH_SITES = ["linkedin", "indeed"]

# How many hours back to look (168 = 7 days, 72 = 3 days, 24 = 1 day)
HOURS_OLD = 168

# Max results to scrape per query per job site
RESULTS_PER_QUERY = 25


# ==============================================================================
# 2. SEARCH CATEGORIES & TARGET QUERIES
# ==============================================================================
# Group search queries into logical categories for structured CSV filtering.
SEARCH_CATEGORIES = {
    "AI Operations & Technical Solutions": [
        "AI Operations Specialist", "AI Ops Manager", "AI Ops",
        "Solutions Engineer", "Technical Solutions Architect", 
        "Technical Solutions Specialist", "Implementation Specialist"
    ],
    "Deployment & Tech Ops": [
        "Deployment Generalist", "Technical Deployment Manager", 
        "Deployment Specialist", "Technical Operations", "Tech Ops Specialist"
    ],
    "Product Operations (Product Ops)": [
        "Product Operations Specialist", "Product Ops", 
        "Technical Product Operator", "Technical Product Operations"
    ],
    "Technical Growth & Growth Ops": [
        "Technical Growth Specialist", "Growth Hacker", 
        "Growth Operations", "Growth Specialist"
    ],
    "Office, Front Desk & People Operations": [
        "Front Desk", "Front Desk Coordinator", "Front Office Coordinator", 
        "Receptionist", "Office Assistant", "Administrative Assistant", 
        "Office Manager", "People Associate", "People Operations", 
        "People Ops", "Workplace Experience Coordinator", 
        "Guest Services Coordinator", "HR Coordinator"
    ],
    "Founder Support & Generalist": [
        "Founder Associate", "Founders Associate", "Special Projects", 
        "Generalist", "Open Application", "Talent Pool"
    ]
}


# ==============================================================================
# 3. TITLE-BASED EXCLUSION KEYWORDS
# ==============================================================================
# Jobs containing ANY of these words/phrases in their title will be immediately dropped.
EXCLUDE_TITLE_KEYWORDS = [
    # Senior / Executive roles
    "senior", "lead", "director", "head of", "principal", "vp", "chief", "sr.", "sr ", "sr-",
    
    # Software Engineering & Deep Data Science
    "software engineer", "backend", "frontend", "fullstack", "architect", "developer", "devops",
    "applied scientist", "applied science", "machine learning", "ml engineer",
    
    # Unrelated domains (accounting, legal, etc.)
    "accountant", "buchhalter", "payroll", "legal counsel",
    
    # Internships / Student jobs
    "intern", "internship", "working student", "werkstudent", "praktikant"
]


# ==============================================================================
# 4. LANGUAGE EXCLUSION FILTERING (REGEX PRESETS)
# ==============================================================================
# Filter out jobs requiring local language proficiency (for strictly English-speaking roles).

# --- Preset: GERMAN Language Exclusion ---
GERMAN_REGEX_PATTERNS = [
    r'\b(native|mother\s*tongue|muttersprache)\b.*\b(german|deutsch)\b',
    r'\b(german|deutsch)\b.*\b(native|mother\s*tongue|muttersprache)\b',
    r'\b(fluent|fluency|fließend|fliessend|fließende|fliessende|fließendem)\b.*\b(german|deutsch)\b',
    r'\b(german|deutsch)\b.*\b(fluent|fluency|fließend|fliessend|fließende|fliessende)\b',
    r'\b(proficiency|proficient|advanced)\b.*\b(german|deutsch)\b',
    r'\b(german|deutsch)\b.*\b(proficiency|proficient|advanced)\b',
    r'\b(german|deutsch)\b.*\b(c1|c2|b2|niveau)\b',
    r'\b(c1|c2|b2)\b.*\b(german|deutsch)\b',
    r'\b(german|deutsch)\b\s*(&|and|und)\s*\b(english|englisch)\b',
    r'\b(english|englisch)\b\s*(&|and|und)\s*\b(german|deutsch)\b',
    r'\b(sehr\s+gute|gute|excellent|verhandlungssicher)\b.*\b(german|deutsch)\b',
    r'\b(german|deutsch)\b.*\b(erforderlich|voraussetzung|mandatory|must)\b',
    r'fließende\s+deutsch', r'fliessende\s+deutsch', r'deutschkenntnisse', r'must\s+speak\s+german'
]

# --- Preset: SPANISH Language Exclusion (Example for Spain/LATAM) ---
SPANISH_REGEX_PATTERNS = [
    r'\b(nativo|lengua\s*materna|idioma\s*materno)\b.*\b(español|castellano|spanish)\b',
    r'\b(español|castellano|spanish)\b.*\b(nativo|lengua\s*materna)\b',
    r'\b(fluido|fluidez|bilingüe|avanzado)\b.*\b(español|castellano|spanish)\b',
    r'\b(español|castellano|spanish)\b.*\b(fluido|fluidez|bilingüe|avanzado|imprescindible|requisito)\b',
    r'\b(español|castellano)\b.*\b(c1|c2|b2|nivel)\b',
    r'\b(c1|c2|b2)\b.*\b(español|castellano)\b',
    r'\b(español|castellano)\b\s*(&|and|y)\s*\b(inglés|english)\b',
    r'\b(inglés|english)\b\s*(&|and|y)\s*\b(español|castellano)\b',
    r'español\s+imprescindible', r'spanish\s+required', r'must\s+speak\s+spanish'
]

# --- Preset: FRENCH Language Exclusion (Example for France/Belgium) ---
FRENCH_REGEX_PATTERNS = [
    r'\b(natif|langue\s*maternelle)\b.*\b(français|french)\b',
    r'\b(français|french)\b.*\b(courant|bilingue|avancé|exigé|obligatoire)\b',
    r'\b(français|french)\b.*\b(c1|c2|b2|niveau)\b',
    r'\b(c1|c2|b2)\b.*\b(français|french)\b',
    r'français\s+exigé', r'french\s+required', r'must\s+speak\s+french'
]

# Active language exclusion patterns (Change to SPANISH_REGEX_PATTERNS, FRENCH_REGEX_PATTERNS, or [] to disable)
ACTIVE_LANGUAGE_PATTERNS = GERMAN_REGEX_PATTERNS


# ==============================================================================
# 5. CANDIDATE PROFILE KEYWORDS (MATCH SCORING)
# ==============================================================================
# Keywords reflecting your background and target skillset.
# The more of these keywords appear in the job description, the higher the Match Score (0-100%).
PROFILE_KEYWORDS = [
    "generalist", "operations", "ai", "automation", "n8n", "ux", "ui", "mvp", 
    "troubleshooting", "solutions", "product", "deployment", "implementation", 
    "crisis", "logistics", "broadcast", "video", "founder", "workflow", "no-code"
]


# ==============================================================================
# 6. HISTORICAL REVIEW TRACKING KEYWORDS
# ==============================================================================
# Keywords in any spreadsheet column or cell that designate a job as "reviewed" / "handled"
REVIEWED_STATUS_KEYWORDS = [
    "applied", "rejected", "interview", "offer", "passed", "declined", "reviewed", 
    "no", "skip", "done", "submitted", "отклик", "отказ", "интервью", "просмотрено", "пропуск"
]


# ==============================================================================
# 7. SYSTEM & SCRAPER SETTINGS
# ==============================================================================
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Preferred column order for exported CSV files
OUTPUT_COLUMNS = [
    'match_score', 'category', 'title', 'company', 'contact_email', 
    'location', 'site', 'search_query', 'job_url', 'date_posted', 'description'
]
