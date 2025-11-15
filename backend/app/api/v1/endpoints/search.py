"""
Search endpoints - Unified search across all modules.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db_sync
from app.auth import get_current_user
from app.models.user import User
from app.services.search_service import UnifiedSearchService

router = APIRouter()


@router.get("/search")
def search_all(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """
    Search across all modules (tasks, finance, documents, marketing).
    Returns results grouped by module type.
    """
    service = UnifiedSearchService(db)
    return service.search_all(current_user.id, q, limit)


@router.get("/search/{search_type}")
def search_by_type(
    search_type: str,
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """
    Search in specific module only.
    search_type: tasks, finance, documents, marketing
    """
    service = UnifiedSearchService(db)
    results = service.search_by_type(current_user.id, q, search_type, limit)
    return {"type": search_type, "results": results}


@router.get("/recent")
def get_recent_activity(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Get recent activity across all modules."""
    service = UnifiedSearchService(db)
    return service.get_recent_activity(current_user.id, days, limit)
