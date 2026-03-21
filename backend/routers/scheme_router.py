"""Scheme router for listing and explanation endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/schemes", tags=["schemes"])
