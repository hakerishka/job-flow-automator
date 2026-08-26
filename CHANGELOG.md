# 📜 Changelog

All notable changes to **Job-Flow Automator** are documented in this file.
This project adheres to [Semantic Versioning](https://semver.org/).

---

## [1.2.0] — 2026-08-26

### 🚀 Added
- **Multi-Track Match Scoring Engine:** Deterministic, regex-based scoring across 4 tracks (*AI & Workflow Automation*, *Technical Operations*, *Media & AV*, *Workplace & Generalist*) with word-boundary evaluation, signature tool tiers, and penalty rules.
- **Strict Location & Geographic Validator:** Smart filter (`is_valid_location`) accepting Berlin/Potsdam and EU-accessible Remote while dropping foreign hybrid/onsite roles.
- **Model Context Protocol (MCP) & Neural Voiceover Profile:** Expanded Master CV and experience bank with book translation, audiobook cloning, and Windows deep cleaner projects.
- **Comprehensive Pytest Suite:** Full unit and integration test coverage (`tests/test_config.py`, `tests/test_scoring.py`, `tests/test_custom_boards.py`, `tests/test_pipeline.py`).
- **GitHub Actions CI Pipeline:** Automated cross-platform (Ubuntu/Windows) testing across Python 3.10, 3.11, 3.12.
- **Dynamic Live Stream Detection:** Process-based PID lockfile inspection (`.scraper.lock`) in Streamlit UI.

### 🔧 Fixed
- Fixed false-positive matches for `ai`, `av`, and `obs` inside arbitrary English words.
- Fixed stream state caching bug in Streamlit with `importlib.reload(config)`.

---

## [1.1.0] — 2026-08-24

### 🚀 Added
- **AshbyHQ & Greenhouse Direct APIs:** High-speed REST connectors for top AI scaleups and European VC unicorn portfolios.
- **Arbeitnow API & Berlin Startup Jobs RSS:** Real-time tech posting feeds.
- **Typst PDF Typesetting Engine:** Dynamic, pixel-perfect 1-page PDF generation.
- **Cumulative Review Tracker:** Spreadsheet scanner detecting colored cell rows and status tags.

---

## [1.0.0] — 2026-08-01

### 🚀 Added
- Initial release with JobSpy scraping, Streamlit UI, and 2-phase Gemini ATS tailoring.
