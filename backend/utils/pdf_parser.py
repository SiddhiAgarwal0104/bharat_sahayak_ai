
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
        "raw_text":             raw_text[:4000],   # used for embedding
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
    """
    Derive category from filename prefix.
    e.g. health_ayushman_bharat_guidelines.pdf -> health
    """
    name = filename.lower()
    if name.startswith("health"):
        return "health"
    if name.startswith("pension"):
        return "pension"
    if name.startswith("agriculture") or name.startswith("agri"):
        return "agriculture"
    if name.startswith("women") or name.startswith("woman"):
        return "women"
    # fallback: use first word before underscore
    return name.split("_")[0]


def _extract_name(text: str, filename: str) -> str:
    """
    Try to find scheme name from the first few lines of the PDF.
    Falls back to filename-derived name.
    """
    # Try first 600 characters — scheme name is usually the title
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
    sections. Falls back to first 800 chars.
    """
    text_lower = text.lower()

    keywords = ["objective", "about the scheme", "introduction", "overview",
                "background", "scheme overview", "about"]

    for kw in keywords:
        idx = text_lower.find(kw)
        if idx != -1:
            # Take text from that keyword onward, up to 800 chars
            snippet = text[idx: idx + 800].strip()
            return snippet

    # Fallback: first 800 chars
    return text[:800].strip()


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
    # Patterns: "18 to 60 years", "age between 18-70", "18-60 years"
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
    # Patterns: "income below rs. 2,00,000", "annual income not exceeding 1.5 lakh"
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
                # If it looks like lakhs (small number like 2, 1.5)
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
    """
    text_lower = text.lower()
    keywords = ["benefit", "financial assistance", "subsidy", "grant amount",
                "pension amount", "insurance cover", "cash transfer", "amount of"]

    for kw in keywords:
        idx = text_lower.find(kw)
        if idx != -1:
            return text[max(0, idx - 30): idx + 500].strip()

    # Fallback: text between chars 800–1400
    return text[800:1400].strip()


def _extract_docs(text: str) -> str:
    """
    Find the documents required section.
    """
    text_lower = text.lower()
    keywords = ["documents required", "required documents", "documents needed",
                "list of documents", "following documents", "attach", "enclose"]

    for kw in keywords:
        idx = text_lower.find(kw)
        if idx != -1:
            return text[idx: idx + 600].strip()

    return "Please refer to the scheme PDF for document requirements."
