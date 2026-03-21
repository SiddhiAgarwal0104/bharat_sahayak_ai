"""
scheme.py  —  MongoDB version
------------------------------
No SQLAlchemy table. Schemes are stored as plain dicts in MongoDB.
This file defines the shape of a scheme document and helper functions.
Member 3 owns this file.
"""

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
    """
    Returns a scheme dict ready to insert into MongoDB.
    Shape matches what the rest of the code expects.
    """
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
    """
    Convert a MongoDB document to a clean dict for API responses.
    Converts ObjectId to string so it can be JSON serialised.
    """
    if doc is None:
        return None
    result = dict(doc)
    if "_id" in result:
        result["id"] = str(result.pop("_id"))
    return result
