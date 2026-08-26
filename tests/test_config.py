"""
Unit Tests for config.py (Geographic Validation, Language Regexes, Title Exclusions).
"""
import pytest
import config


class TestLocationValidator:
    """Tests for config.is_valid_location()."""

    @pytest.mark.parametrize("loc,title,expected", [
        ("Berlin, Germany", "AI Specialist", True),
        ("Berlin", "Solutions Engineer", True),
        ("Potsdam, Brandenburg, Germany", "Ops Specialist", True),
        ("Linienstr. 214 10119 Berlin, Germany", "Manager", True),
        ("Berlin Office | London | Belgrade", "Developer", True),
        ("Berlin / Remote", "DevOps", True),
        ("Remote (EMEA)", "Workflow Automation", True),
        ("Remote, Germany", "Prompt Engineer", True),
        ("Deutschland Remote", "Tech Ops", True),
        ("Europe", "Operations Generalist", True),
        ("Worldwide", "Automation Lead", True),
    ])
    def test_valid_locations_accepted(self, loc, title, expected):
        assert config.is_valid_location(loc, title_str=title) is True

    @pytest.mark.parametrize("loc,title,wp,expected", [
        ("San Francisco, CA", "Solutions Engineer", None, False),
        ("London, United Kingdom", "Tech Ops", None, False),
        ("Munich, Germany", "Client Value Partner", None, False),
        ("Frankfurt am Main, Hesse, Germany", "Specialist", None, False),
        ("Remote, US, California", "Account Exec", None, False),
        ("United States", "Engineer", None, False),
        ("Singapore", "Test Engineer", None, False),
        ("Toronto, Ontario, Canada", "Support Engineer", None, False),
        ("Munich", "Operator", "Hybrid", False),
        ("London Office", "Engineer", "Onsite", False),
        ("Remote", "Technical Customer Success - Americas", None, False),
        ("Remote", "B2B Field Marketer - LATAM", None, False),
        ("Remote (US)", "Engineer", None, False),
        ("US - Remote", "Engineer", None, False),
        ("", "Engineer", None, False),
    ])
    def test_invalid_locations_rejected(self, loc, title, wp, expected):
        assert config.is_valid_location(loc, title_str=title, workplace_type=wp) is False


class TestLanguageExclusionRegex:
    """Tests for local language requirement detection."""

    @pytest.mark.parametrize("text,expected_match", [
        ("Fluent German and English required for this position.", True),
        ("Fließende Deutschkenntnisse in Wort und Schrift (C1 Niveau).", True),
        ("Muttersprache Deutsch oder verhandlungssicher erforderlich.", True),
        ("This is a 100% English speaking company. No German needed.", False),
        ("Working proficiency in English is our working language.", False),
        ("You will work with an international team across Europe.", False),
    ])
    def test_german_language_detection(self, text, expected_match):
        matched = any(bool(config.re.search(pat, text.lower(), config.re.DOTALL)) for pat in config.GERMAN_REGEX_PATTERNS)
        assert matched is expected_match


class TestTitleExclusionKeywords:
    """Tests for title filtering (Senior, Intern, Software Dev, Medical)."""

    @pytest.mark.parametrize("title,is_excluded", [
        ("Senior Software Engineer", True),
        ("VP of Engineering", True),
        ("Head of Product Operations", True),
        ("Principal Architect", True),
        ("Lead Developer", True),
        ("Working Student Marketing (Werkstudent)", True),
        ("Internship - Data Science", True),
        ("Buchhalter / Accountant", True),
        ("Staff Backend Developer (Golang)", True),
        ("AI Operations Specialist", False),
        ("Technical Solutions Specialist", False),
        ("Deployment Coordinator", False),
        ("Workflow Automation Specialist", False),
        ("Livestream & AV Producer", False),
        ("Operations Generalist", False),
    ])
    def test_title_exclusions(self, title, is_excluded):
        t_low = title.lower()
        has_bad_keyword = any(bad in t_low for bad in config.EXCLUDE_TITLE_KEYWORDS)
        assert has_bad_keyword is is_excluded
