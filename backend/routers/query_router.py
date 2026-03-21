"""Query router exposing the main /query endpoint."""

from fastapi import APIRouter

router = APIRouter(prefix="/query", tags=["query"])
