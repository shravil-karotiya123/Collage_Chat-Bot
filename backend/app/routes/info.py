"""
College Information Route Handlers.
"""

from fastapi import APIRouter
from app.services.bot_service import COLLEGE_KNOWLEDGE

router = APIRouter(prefix="/api/info", tags=["Information"])


@router.get("/courses")
def get_courses():
    return {"courses": COLLEGE_KNOWLEDGE["courses"]}


@router.get("/admissions")
def get_admissions():
    return {"admissions": COLLEGE_KNOWLEDGE["admissions"]}


@router.get("/placements")
def get_placements():
    return {"placements": COLLEGE_KNOWLEDGE["placements"]}


@router.get("/faq")
def get_faqs():
    return {"faqs": COLLEGE_KNOWLEDGE["faqs"]}
