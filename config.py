"""
⚙️ CONFIGURATION FILE
Central settings for job search, filtering, language exclusion, scoring, and review tracking.
Easily adapt this pipeline for any location, language, or job domain.
"""

import re

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

# --- LOCATION VALIDATION & SMART GEOGRAPHIC FILTERING ---
TARGET_LOCATIONS = ["berlin", "potsdam", "brandenburg"]

# Non-target regions, countries, and cities that disqualify a listing unless Berlin is explicitly in the location
EXCLUDED_LOCATION_PATTERNS = [
    # US / Americas / LATAM
    r'\bsan francisco\b', r'\bsf\b', r'\bsan jose\b', r'\bcalifornia\b', r'\bnew york\b', r'\bnyc\b',
    r'\bseattle\b', r'\baustin\b', r'\btexas\b', r'\bboston\b', r'\bmassachusetts\b', r'\blos angeles\b',
    r'\bchicago\b', r'\billinois\b', r'\bwashington\b', r'\batlanta\b', r'\bcolorado\b', r'\bdenver\b',
    r'\bunited states\b', r'\bus\s*-\s*remote', r'\bremote,\s*us\b', r'\bremote\s*\(us\)', r'\b\(us\)',
    r'\bremote\s+in\s+the\s+us\b', r'\bremote\s+in\s+us\b', r'\bus\s+only\b', r'\bnorth america\b',
    r'\bamericas?\b', r'\busa\b', r'\bus\b',
    r'\bcanada\b', r'\btoronto\b', r'\bvancouver\b', r'\bontario\b', r'\bmontreal\b',
    r'\bmexico\b', r'\bbrazil\b', r'\bsão paulo\b', r'\bsao paulo\b', r'\bcolombia\b', r'\bargentina\b',
    r'\bchile\b', r'\blatam\b',
    
    # UK & Other European non-Berlin cities / countries
    r'\blondon\b', r'\bunited kingdom\b', r'\buk\s*-\s*remote', r'\bremote,\s*uk\b',
    r'\bremote\s*\(uk\)', r'\bhybrid\s*\(uk\)', r'\b\(uk\)', r'\buk\s+only\b', r'\buk\b',
    r'\bengland\b', r'\bscotland\b', r'\bwales\b',
    r'\bcambridge\b', r'\boxford\b', r'\bmanchester\b', r'\bedinburgh\b', r'\bdublin\b', r'\bireland\b',
    r'\bmunich\b', r'\bmünchen\b', r'\bfrankfurt\b', r'\bhamburg\b', r'\bcologne\b', r'\bköln\b',
    r'\bstuttgart\b', r'\bdüsseldorf\b', r'\bduesseldorf\b', r'\bleipzig\b', r'\bdresden\b',
    r'\bnuremberg\b', r'\bnürnberg\b', r'\bbonn\b', r'\bleverkusen\b', r'\bsaarbrücken\b', r'\bdarmstadt\b',
    r'\bvienna\b', r'\bwien\b', r'\baustria\b', r'\bösterreich\b', r'\bzurich\b', r'\bzürich\b', r'\bswitzerland\b', r'\bschweiz\b',
    r'\bparis\b', r'\bfrance\b', r'\bmadrid\b', r'\bbarcelona\b', r'\bspain\b', r'\bespaña\b',
    r'\bmilan\b', r'\bmilano\b', r'\brome\b', r'\broma\b', r'\bitaly\b', r'\bitalia\b',
    r'\bamsterdam\b', r'\bnetherlands\b', r'\blisbon\b', r'\blisboa\b', r'\bportugal\b',
    r'\bpoland\b', r'\bwarsaw\b', r'\bpolska\b', r'\bcracow\b', r'\bkrakow\b', r'\bwrocław\b',
    r'\bromania\b', r'\bbucharest\b', r'\bbulgaria\b', r'\bsofia\b', r'\bhungary\b', r'\bbudapest\b',
    r'\bcroatia\b', r'\bserbia\b', r'\bbelgrade\b', r'\bukraine\b', r'\bkyiv\b', r'\bkiev\b',
    r'\bstockholm\b', r'\bsweden\b', r'\bcopenhagen\b', r'\bdenmark\b',
    r'\bhelsinki\b', r'\bfinland\b', r'\boslo\b', r'\bnorway\b', r'\bbrussels\b', r'\bbelgium\b',
    r'\bprague\b', r'\bczechia\b', r'\bczech\b', r'\bgreece\b', r'\bathens\b',
    
    # Asia / Pacific / Middle East / Africa
    r'\bsydney\b', r'\bmelbourne\b', r'\baustralia\b', r'\bsingapore\b', r'\btokyo\b', r'\bjapan\b',
    r'\bseoul\b', r'\bsouth korea\b', r'\bkorea\b', r'\bchina\b', r'\bbeijing\b', r'\bshanghai\b',
    r'\bindia\b', r'\bbangalore\b', r'\bbengaluru\b', r'\bmumbai\b', r'\bdelhi\b', r'\bhyderabad\b',
    r'\bsaudi arabia\b', r'\briyadh\b', r'\bunited arab emirates\b', r'\buae\b', r'\bdubai\b', r'\babu dhabi\b',
    r'\bqatar\b', r'\bkuwait\b', r'\bbahrain\b', r'\boman\b', r'\bisrael\b', r'\btel aviv\b',
    r'\bapac\b', r'\basia\b', r'\bafrica\b'
]


def is_valid_location(location_str, title_str="", workplace_type=None, is_remote=None):
    """
    Validate whether a job is based in Berlin/Potsdam or is an acceptable EU/Germany-accessible Remote role.
    Strictly filters out non-Berlin hybrid/onsite roles and geographically restricted non-EU remote roles.
    """
    loc = str(location_str).lower().strip() if location_str else ""
    title = str(title_str).lower().strip() if title_str else ""
    wp = str(workplace_type).lower().strip() if workplace_type else ""
    combined = f"{loc} {title}"

    # 1. Target Hub Match (Berlin / Potsdam / Brandenburg)
    if any(t in loc for t in TARGET_LOCATIONS):
        return True

    # 2. Strict check: If Hybrid or Onsite in any non-Berlin location -> DISQUALIFY
    if wp in ["hybrid", "onsite", "in-office", "in office", "office"]:
        return False
    if "hybrid" in loc or "on-site" in loc or "onsite" in loc or "in-office" in loc or "office" in loc:
        return False

    # 3. Check for explicitly excluded foreign regions/cities/timezones
    for pat in EXCLUDED_LOCATION_PATTERNS:
        if re.search(pat, combined):
            return False

    # 4. Check for Valid Remote for EU / Germany / General Remote
    if any(r in loc for r in ["remote", "emea", "europe", "germany", "deutschland", "anywhere", "worldwide", "global"]):
        return True

    if is_remote is True or wp == "remote":
        if not loc or any(r in loc for r in ["remote", "emea", "europe", "germany", "deutschland", "anywhere", "worldwide", "global"]):
            return True

    # 5. Default reject if no Berlin or explicit valid Remote indicator
    return False


# ==============================================================================
# 2. SEARCH CATEGORIES & TARGET QUERIES
# ==============================================================================
SEARCH_CATEGORIES = {
    "AI Operations & Technical Solutions": [
        "AI Operations Specialist", "AI Ops Manager", "AI Ops",
        "Solutions Engineer", "Technical Solutions Architect", 
        "Technical Solutions Specialist", "Implementation Specialist",
        "Workflow Automation Specialist", "n8n Specialist", "No-Code Specialist", "Prompt Engineer"
    ],
    "Deployment & Tech Ops": [
        "Deployment Generalist", "Technical Deployment Manager", 
        "Deployment Specialist", "Technical Operations", "Tech Ops Specialist",
        "IT Operations Coordinator"
    ],
    "Product Operations (Product Ops)": [
        "Product Operations Specialist", "Product Ops", 
        "Technical Product Operator", "Technical Product Operations",
        "Technical Project Coordinator"
    ],
    "Live Video, Streaming & Broadcast Operations": [
        "Livestream Operator", "Live Streaming Engineer", "Broadcast Technician",
        "Broadcast Engineer", "Studio Technician", "Control Room Operator",
        "Vision Mixer", "vMix Operator", "Webinar Producer",
        "Virtual Events Producer", "Hybrid Events Technician", "AV Technician",
        "Video Operations Specialist", "Video Editor", "Multimedia Producer"
    ],
    "IT Support & Workplace Operations": [
        "IT Support Specialist", "Technical Support Specialist", "Technical Support Engineer",
        "Helpdesk Specialist", "First Level Support", "Desktop Support Technician",
        "Workplace Experience Specialist", "Corporate IT Coordinator", "Endpoint Management"
    ],
    "Office, Front Desk & People Operations": [
        "Front Desk", "Front Desk Coordinator", "Front Office Coordinator", 
        "Receptionist", "Office Assistant", "Administrative Assistant", 
        "Office Manager", "People Associate", "People Operations", 
        "People Ops", "Workplace Experience Coordinator", 
        "Guest Services Coordinator"
    ],
    "Generalist & Special Projects": [
        "Special Projects", "Generalist", "Operations Generalist", 
        "Open Application"
    ]
}


# ==============================================================================
# 3. TITLE-BASED EXCLUSION KEYWORDS
# ==============================================================================
# Jobs containing ANY of these words/phrases in their title will be immediately dropped.
EXCLUDE_TITLE_KEYWORDS = [
    # Senior / Executive / C-level roles
    "senior", "lead", "director", "head of", "principal", "vp", "chief", "sr.", "sr ", "sr-",
    
    # Software Engineering & Heavy Data Science
    "software engineer", "backend", "frontend", "fullstack", "architect", "developer", "devops",
    "applied scientist", "applied science", "machine learning", "ml engineer",
    
    # High-exhaustion Sales, Customer Success & Cold Outreach (Avoid burnout)
    "customer success manager", "account manager", "sales development", "sdr", "bdr", 
    "account executive", "sales executive", "vertrieb", "outbound", "cold call", "telemarketing",
    
    # Unrelated domains (medical, accounting, legal)
    "accountant", "buchhalter", "payroll", "legal counsel", "pflege", "nurse", "arzt",
    
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
# 5. MULTI-TRACK CANDIDATE PROFILE & SCORING ENGINE
# ==============================================================================
# Multi-track weighted scoring engine with word-boundary regexes, title bonuses,
# signature tool tiers, and hard engineering requirement penalties.

SCORING_TRACKS = {
    "AI & Workflow Automation": {
        "title_keywords": [
            r'\bai\s+ops\b', r'\bai\s+operations\b', r'\bworkflow\s+automation\b',
            r'\bsolutions?\s+engine(?:er|ering)\b', r'\bsolutions?\s+specialist\b',
            r'\bprompt\s+engineer\b', r'\bno-code\b', r'\bautomation\s+specialist\b',
            r'\bautomation\s+engineer\b', r'\bautomation\s+manager\b',
            r'\bn8n\b', r'\bmake\b', r'\bzapier\b', r'\bprocess\s+automation\b',
            r'\bimplementation\s+specialist\b', r'\btechnical\s+solutions\b'
        ],
        "tier1_tools": [  # 20 pts each
            (r'\bn8n\b', "n8n"),
            (r'\bmake\.com\b|\bintegromat\b', "Make.com"),
            (r'\bzapier\b', "Zapier"),
            (r'\bprompt\s+engineering\b|\bprompting\b', "Prompt Engineering"),
            (r'\bno-?code\b|\blow-?code\b', "No-Code/Low-Code"),
            (r'\bworkflow\s+automation\b|\bprocess\s+automation\b', "Workflow Automation"),
            (r'\bai\s+agents?\b|\bllms?\b|\blarge\s+language\s+models?\b', "LLMs/AI"),
            (r'\bai\s+operations\b|\bai\s+ops\b', "AI Ops")
        ],
        "tier2_skills": [  # 10 pts each
            (r'\bprocess\s+optimization\b|\bprocess\s+improvement\b', "Process Optimization"),
            (r'\bapi\s+integrations?\b|\bwebhooks?\b|\brest\s+apis?\b', "API & Webhooks"),
            (r'\bsolutions?\s+architecture\b|\bsolutions?\s+engineering\b', "Solutions Eng"),
            (r'\bimplementation\b', "Implementation"),
            (r'\bproduct\s+ops\b|\btechnical\s+operations\b', "Product/Tech Ops"),
            (r'\bmvp\b|\bprototyping\b', "MVP/Prototyping")
        ]
    },
    "Technical Operations & Deployment": {
        "title_keywords": [
            r'\bdeployment\b', r'\btechnical\s+operations\b', r'\btech\s+ops\b',
            r'\bit\s+operations\b', r'\bit\s+support\b', r'\boperations\s+coordinator\b',
            r'\btechnical\s+deployment\b', r'\boperations\s+specialist\b',
            r'\bsolutions?\s+specialist\b', r'\bimplementation\b', r'\bit\s+specialist\b'
        ],
        "tier1_tools": [  # 20 pts each
            (r'\btechnical\s+deployment\b|\bdeployment\s+specialist\b', "Deployment"),
            (r'\bsystem\s+integration\b|\bsystems?\s+integration\b', "System Integration"),
            (r'\bit\s+support\b|\btechnical\s+support\b|\bhelpdesk\b', "IT/Tech Support"),
            (r'\btroubleshooting\b|\bincident\s+management\b', "Troubleshooting"),
            (r'\bonboarding\b|\bhardware\s+setup\b', "Onboarding/Hardware"),
            (r'\btechnical\s+documentation\b|\btechnical\s+writer\b|\btechnical\s+writing\b', "Tech Writing")
        ],
        "tier2_skills": [  # 10 pts each
            (r'\bsaas\s+administration\b|\bgoogle\s+workspace\b|\bslack\b|\bjira\b', "SaaS/Workspace Admin"),
            (r'\bcustomer\s+onboarding\b|\brollout\b', "Rollout & Ops"),
            (r'\bprocess\s+improvement\b|\bworkflows?\b', "Workflow Ops"),
            (r'\bvendor\s+management\b|\bitil\b', "IT Operations"),
            (r'\bqa\b|\bquality\s+assurance\b|\btesting\b', "QA & Testing")
        ]
    },
    "Media, AV & Livestream Operations": {
        "title_keywords": [
            r'\bav\b', r'\baudiovisual\b', r'\blivestream\b', r'\bvideo\b',
            r'\bbroadcast\b', r'\bstreaming\b', r'\bwebinar\b', r'\bmedia\s+production\b',
            r'\bproduction\s+specialist\b', r'\bmedia\s+ops\b'
        ],
        "tier1_tools": [  # 20 pts each
            (r'\bvmix\b', "vMix"),
            (r'\bobs\s+studio\b|\bobs\b', "OBS Studio"),
            (r'\bndi\b|\bsrt\b|\brtmp\b', "NDI/SRT/RTMP"),
            (r'\blivestream(?:ing)?\b|\bbroadcast(?:ing)?\b', "Livestream/Broadcast"),
            (r'\baudiovisual\b|\bav\s+technician\b|\bav\s+support\b', "Audiovisual (AV)"),
            (r'\bwebinars?\b|\bvirtual\s+events?\b', "Webinars/Virtual Events"),
            (r'\bvideo\s+production\b|\bvideo\s+editing\b', "Video Production")
        ],
        "tier2_skills": [  # 10 pts each
            (r'\baudio\s+mixing\b|\bdante\b', "Audio Engineering"),
            (r'\blighting\b|\bcameras?\b|\bvideo\s+switcher\b', "Studio Hardware"),
            (r'\bpost-?production\b|\bpremiere\b|\bdavinci\b', "Post-Production"),
            (r'\bevent\s+technology\b|\btechnical\s+director\b', "Event Technology")
        ]
    },
    "Workplace & Operations Generalist": {
        "title_keywords": [
            r'\bworkplace\b', r'\bfront\s+desk\b', r'\breceptionist\b', r'\boffice\s+assistant\b',
            r'\boffice\s+manager\b', r'\bpeople\s+operations\b', r'\bpeople\s+ops\b',
            r'\boperations\s+generalist\b', r'\bspecial\s+projects\b', r'\bgeneralist\b'
        ],
        "tier1_tools": [  # 20 pts each
            (r'\bworkplace\s+experience\b|\bworkplace\s+coordinator\b', "Workplace Experience"),
            (r'\bfront\s+desk\b|\bguest\s+services\b|\breception\b', "Front Desk"),
            (r'\boffice\s+management\b|\boffice\s+operations\b', "Office Ops"),
            (r'\bpeople\s+operations\b|\bpeople\s+ops\b', "People Ops"),
            (r'\boperations\s+generalist\b|\bspecial\s+projects\b', "Operations Generalist")
        ],
        "tier2_skills": [  # 10 pts each
            (r'\bevent\s+coordination\b|\bteam\s+events\b', "Event Coordination"),
            (r'\bfacilities\b|\bvendor\s+coordination\b', "Facilities"),
            (r'\bonboarding\s+experience\b', "Onboarding Support"),
            (r'\bcross-functional\b|\bproject\s+coordination\b', "Project Coordination")
        ]
    }
}

COMMON_SUPPORTING_SKILLS = [
    (r'\btroubleshooting\b', "Troubleshooting"),
    (r'\bdocumentation\b|\bsops?\b', "Documentation"),
    (r'\bagile\b|\bscrum\b|\bkanban\b', "Agile/Scrum"),
    (r'\bcommunication\s+skills?\b', "Communication")
]

HARD_REQUIREMENT_PENALTIES = [
    (r'\b(5\+|7\+|10\+)\s+years\s+(?:of\s+)?(?:software\s+development|programming|backend|frontend|java|c\+\+|rust|golang)\b', "5+ yrs Deep Software Dev"),
    (r'\b(java|c\+\+|rust|golang|scala)\s+expert\b', "Expert Low-Level Language"),
    (r'\bkubernetes\s+cluster\s+management\b|\bterraform\s+infrastructure\b', "Heavy DevOps/Infra"),
    (r'\bcold\s+calling\s+quota\b|\btelemarketing\b|\boutbound\s+sales\s+quota\b', "Cold Sales Quota")
]


def evaluate_job_match(title, description):
    """
    Calculate deterministic, multi-track match score (0-100%) and extract matched skill tags.
    """
    t_lower = str(title).lower() if title else ""
    d_lower = str(description).lower() if description else ""
    combined = f"{t_lower} {d_lower}"
    
    # Calculate penalty
    penalty = 0
    penalty_reasons = []
    for pat, label in HARD_REQUIREMENT_PENALTIES:
        if re.search(pat, combined):
            penalty += 25
            penalty_reasons.append(label)

    best_score = 0
    best_track = "General Operations"
    best_tags = []

    # Common supporting skills
    common_tags = []
    common_pts = 0
    for pat, label in COMMON_SUPPORTING_SKILLS:
        if re.search(pat, combined):
            common_tags.append(label)
            common_pts += 3

    for track_name, track_data in SCORING_TRACKS.items():
        track_score = 0
        track_tags = []

        # 1. Title Bonus (35 pts if title matches track core query)
        title_matched = any(re.search(pat, t_lower) for pat in track_data["title_keywords"])
        if title_matched:
            track_score += 35

        # 2. Tier 1 Tools (20 pts each, max 40 pts)
        tier1_pts = 0
        for pat, label in track_data["tier1_tools"]:
            if re.search(pat, combined):
                track_tags.append(label)
                tier1_pts += 20
        track_score += min(tier1_pts, 40)

        # 3. Tier 2 Skills (10 pts each, max 20 pts)
        tier2_pts = 0
        for pat, label in track_data["tier2_skills"]:
            if re.search(pat, combined):
                track_tags.append(label)
                tier2_pts += 10
        track_score += min(tier2_pts, 20)

        # 4. Add common supporting skills (max 10 pts)
        track_score += min(common_pts, 10)

        # 5. Apply Penalty
        final_track_score = max(0, track_score - penalty)
        final_track_score = min(100, final_track_score)

        if final_track_score > best_score:
            best_score = final_track_score
            best_track = track_name
            best_tags = list(dict.fromkeys(track_tags + common_tags))

    # If no track scored high, check if it has common operations match
    if best_score == 0 and common_pts > 0:
        best_score = min(common_pts * 3, 25)
        best_tags = common_tags

    return {
        "match_score": int(best_score),
        "matched_track": best_track if best_score > 0 else "Uncategorized",
        "matched_skills": ", ".join(best_tags[:6])
    }


# Backwards-compatible legacy keywords
PROFILE_KEYWORDS = [
    "generalist", "operations", "ai", "automation", "n8n", "make", "zapier", 
    "vmix", "ndi", "obs", "livestream", "broadcast", "video", "streaming", "av", 
    "audiovisual", "webinar", "workplace", "it support", "troubleshooting", 
    "deployment", "implementation", "solutions", "product ops", "no-code", 
    "prompt", "llm", "technical writer", "qa", "mvp", "workflow"
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
    'match_score', 'matched_track', 'matched_skills', 'category', 'title', 'company', 
    'contact_email', 'location', 'site', 'search_query', 'job_url', 'date_posted', 'description'
]
