"""
pdf_parser.py
-------------
Reads a scheme guidelines PDF and extracts structured information.
Member 3 owns this file.

Usage:
    from backend.utils.pdf_parser import extract_scheme_info
    info = extract_scheme_info("data/schemes/health_ayushman_bharat_guidelines.pdf")
"""

import pdfplumber
import os
import re


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------

def extract_scheme_info(pdf_path: str) -> dict:
    """
    Read a guidelines PDF and return a standardised scheme dict.

    Returns:
        {
            name, category, description,
            eligibility_criteria (dict),
            benefits, docs_needed, raw_text
        }
    """
    raw_text = _read_pdf(pdf_path)
    filename = os.path.basename(pdf_path)
    category = _get_category(filename)

    return {
        "name":                 _extract_name(raw_text, filename),
        "category":             category,
        "description":          _extract_description(raw_text),
        "eligibility_criteria": _extract_eligibility(raw_text),
        "benefits":             _extract_benefits(raw_text),
        "docs_needed":          _extract_docs(raw_text),
        "raw_text":             raw_text[:4000],   # used for embedding only
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"  [pdf_parser] Warning: could not read {pdf_path}: {e}")
    # Clean up excess whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _get_category(filename: str) -> str:
    name = filename.lower().replace(".pdf", "").replace(" ", "_")

    KEYWORD_MAP = [
        # Health
        ("health",          "health"),
        ("ayushman",        "health"),
        ("cghs",            "health"),
        ("central_government_health", "health"),
        ("bal_swasthya",    "health"),
        ("janani",          "health"),
        ("rbsk",            "health"),
        ("suraksha_bima",   "health"),
        # Pension
        ("nps",             "pension"),
        ("atal",            "pension"),
        ("epf",             "pension"),
        ("employee_pension","pension"),
        ("old_age",         "pension"),
        ("ups",             "pension"),
        # Agriculture
        ("smam",            "agriculture"),
        ("kisan",           "agriculture"),
        ("kcc",             "agriculture"),
        ("pmksy",           "agriculture"),
        ("pmfby",           "agriculture"),
        ("krishi",          "agriculture"),
        # Women
        ("mahila",          "women"),
        ("sukanya",         "women"),
        ("beti",            "women"),
        ("working_women",   "women"),
        ("matru",           "women"),
        ("vandana",         "women"),
        ("ujjawal",         "women"),
        ("ujjwala",         "women"),
        # Education
        ("central_sector",  "education"),
        ("scholarship",     "education"),
        ("vidya",           "education"),
        # Housing
        ("awas",            "housing"),
        ("hostels",         "housing"),
    ]

    for keyword, category in KEYWORD_MAP:
        if keyword in name:
            return category

    return "other"


def _extract_name(text: str, filename: str) -> str:
    """
    Try to find scheme name from the first few lines of the PDF.
    Falls back to filename-derived name.
    """
    first_chunk = text[:600]

    # Look for ALL CAPS line (common for scheme titles in govt PDFs)
    for line in first_chunk.split("\n"):
        line = line.strip()
        if len(line) > 10 and line.isupper():
            return line[:250]

    # Look for lines with "Scheme" or "Yojana" or "Mission"
    for line in first_chunk.split("\n"):
        line = line.strip()
        keywords = ["scheme", "yojana", "mission", "programme", "program", "abhiyan"]
        if any(k in line.lower() for k in keywords) and len(line) > 8:
            return line[:250]

    # Fallback: first non-empty line
    for line in first_chunk.split("\n"):
        line = line.strip()
        if len(line) > 10:
            return line[:250]

    # Last fallback: convert filename to readable name
    base = filename.replace("_guidelines.pdf", "").replace("_", " ")
    return base.title()


def _extract_description(text: str) -> str:
    """
    Return a meaningful description — look for 'about', 'objective', 'introduction'
    sections.

    Takes text from the keyword up to the next major section heading so the
    full description is captured without an arbitrary character cap.
    Falls back to the first 3000 chars of the document.
    """
    text_lower = text.lower()

    # Section-start keywords to search for description
    desc_keywords = [
        "objective", "about the scheme", "introduction", "overview",
        "background", "scheme overview", "about",
    ]

    # Section-end markers — stop extracting when we hit one of these
    # so we don't bleed into eligibility/documents sections
    end_markers = [
        "eligibility", "who can apply", "beneficiar",
        "documents required", "required documents",
        "how to apply", "application process",
        "benefit", "financial assistance",
    ]

    for kw in desc_keywords:
        idx = text_lower.find(kw)
        if idx == -1:
            continue

        # Search up to 5000 chars from keyword start for an end marker
        search_window = text_lower[idx: idx + 5000]
        end_pos = len(search_window)   # default: take the whole window

        for end_kw in end_markers:
            # Skip if the end_kw is the same as the desc keyword we just found
            if end_kw == kw:
                continue
            em_idx = search_window.find(end_kw)
            # Only use as end marker if it appears after at least 300 chars
            # (avoids cutting off if "benefit" appears in the objective line itself)
            if em_idx != -1 and em_idx > 300 and em_idx < end_pos:
                end_pos = em_idx

        snippet = text[idx: idx + end_pos].strip()
        if len(snippet) > 100:   # must be a real section, not a stray word match
            return snippet

    # Fallback: first 3000 chars (enough for a full description, not a truncated one)
    return text[:3000].strip()


def _extract_eligibility(text: str) -> dict:
    """
    Parse eligibility conditions from PDF text.
    Returns a standardised dict that Member 2's rule engine can check.
    """
    text_lower = text.lower()

    criteria = {
        "min_age":    None,
        "max_age":    None,
        "gender":     None,
        "max_income": None,
        "caste":      None,
        "state":      None,
        "pwd_only":   False,
    }

    # --- Age ---
    age_patterns = [
        r'age[s]?\s*(?:between|of|from)?\s*(\d{1,2})\s*(?:to|-|and)\s*(\d{2,3})\s*year',
        r'(\d{1,2})\s*[-–]\s*(\d{2,3})\s*years?\s*of\s*age',
        r'minimum\s*age[:\s]*(\d{1,2})',
    ]
    for pat in age_patterns:
        m = re.search(pat, text_lower)
        if m:
            try:
                criteria["min_age"] = int(m.group(1))
                if m.lastindex >= 2:
                    criteria["max_age"] = int(m.group(2))
            except (ValueError, IndexError):
                pass
            break

    # Standalone max age
    if criteria["max_age"] is None:
        m = re.search(r'maximum\s*age[:\s]*(\d{2,3})', text_lower)
        if m:
            try:
                criteria["max_age"] = int(m.group(1))
            except ValueError:
                pass

    # --- Gender ---
    if any(p in text_lower for p in ["women only", "female only", "only women",
                                      "only female", "for women", "girl child"]):
        criteria["gender"] = "F"
    elif any(p in text_lower for p in ["men only", "male only", "only men", "only male"]):
        criteria["gender"] = "M"

    # --- Income ---
    income_patterns = [
        r'income[^\d]*rs\.?\s*([\d,]+)',
        r'income[^\d]*inr\s*([\d,]+)',
        r'([\d,]+)\s*(?:per\s*annum|annually|per\s*year)[^\w]*income',
        r'income.*?(\d[\d,]*)\s*(?:lakh|lac)',
    ]
    for pat in income_patterns:
        m = re.search(pat, text_lower)
        if m:
            try:
                raw = m.group(1).replace(",", "")
                val = int(raw)
                if val < 1000:
                    val = val * 100000
                criteria["max_income"] = val
            except ValueError:
                pass
            break

    # --- Caste ---
    caste_list = []
    if "scheduled caste" in text_lower or " sc " in text_lower:
        caste_list.append("SC")
    if "scheduled tribe" in text_lower or " st " in text_lower:
        caste_list.append("ST")
    if "other backward" in text_lower or " obc " in text_lower:
        caste_list.append("OBC")
    if caste_list:
        criteria["caste"] = caste_list

    # --- PWD ---
    if any(p in text_lower for p in ["divyang", "disabled person", "pwd",
                                      "persons with disability", "differently abled"]):
        criteria["pwd_only"] = True

    return criteria


def _extract_benefits(text: str) -> str:
    """
    Find the benefits/amount section of the PDF.
    Captures up to the next major section heading instead of a fixed char count.
    """
    text_lower = text.lower()
    keywords = [
        "benefit", "financial assistance", "subsidy", "grant amount",
        "pension amount", "insurance cover", "cash transfer", "amount of",
    ]

    end_markers = [
        "eligibility", "documents required", "how to apply",
        "application process", "who can apply",
    ]

    for kw in keywords:
        idx = text_lower.find(kw)
        if idx == -1:
            continue

        search_window = text_lower[idx: idx + 2000]
        end_pos = len(search_window)

        for end_kw in end_markers:
            em_idx = search_window.find(end_kw)
            if em_idx != -1 and em_idx > 100 and em_idx < end_pos:
                end_pos = em_idx

        snippet = text[max(0, idx - 30): idx + end_pos].strip()
        if len(snippet) > 50:
            return snippet

    # Fallback: text between chars 800–2000
    return text[800:2000].strip()


def _extract_docs(text: str) -> str:
    """
    Find the documents required section.
    Captures up to the next major section heading instead of a fixed char count.
    """
    text_lower = text.lower()
    keywords = [
        "documents required", "required documents", "documents needed",
        "list of documents", "following documents", "attach", "enclose",
    ]

    end_markers = [
        "how to apply", "application process", "contact", "helpline",
        "grievance", "for more information", "disclaimer",
    ]

    for kw in keywords:
        idx = text_lower.find(kw)
        if idx == -1:
            continue

        search_window = text_lower[idx: idx + 2000]
        end_pos = len(search_window)

        for end_kw in end_markers:
            em_idx = search_window.find(end_kw)
            if em_idx != -1 and em_idx > 100 and em_idx < end_pos:
                end_pos = em_idx

        snippet = text[idx: idx + end_pos].strip()
        if len(snippet) > 30:
            return snippet

    return "Please refer to the scheme PDF for document requirements."