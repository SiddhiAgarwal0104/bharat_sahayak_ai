# backend/models/scheme.py
# Member 3 owns this file — MongoDB document helpers

from bson import ObjectId


def scheme_document(
    name: str,
    category: str,
    description: str,
    eligibility_criteria: dict,
    benefits: str,
    docs_needed: str,
    form_url: str,
    guidelines_pdf_url: str,
    form_pdf_url: str,
    embedding_id: int,
) -> dict:
    """Returns a scheme dict ready to insert into MongoDB."""
    return {
        "name":                 name,
        "category":             category,
        "description":          description,
        "eligibility_criteria": eligibility_criteria,
        "benefits":             benefits,
        "docs_needed":          docs_needed,
        "form_url":             form_url,
        "guidelines_pdf_url":   guidelines_pdf_url,
        "form_pdf_url":         form_pdf_url,
        "embedding_id":         embedding_id,
    }


def format_scheme(doc: dict) -> dict:
    """Convert MongoDB document to clean JSON-serialisable dict."""
    if doc is None:
        return None
    result = dict(doc)
    if "_id" in result:
        result["id"] = str(result.pop("_id"))
    return result
