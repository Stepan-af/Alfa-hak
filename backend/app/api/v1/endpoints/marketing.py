from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db_sync
from app.auth import get_current_user
from app.models.user import User
from app.schemas.marketing import (
    MarketingCampaign,
    MarketingCampaignCreate,
    MarketingCampaignUpdate,
    ContentGenerationRequest,
    ContentGenerationResponse,
    ContentIdeasRequest,
    ContentIdeasResponse,
    CampaignMetrics,
    CampaignStatistics,
    ContentCalendar,
)
from app.services.marketing_service import MarketingService

router = APIRouter()


# === Campaign CRUD ===

@router.post("/campaigns", response_model=MarketingCampaign, status_code=201)
def create_campaign(
    campaign: MarketingCampaignCreate,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Создать новую маркетинговую кампанию"""
    return MarketingService.create_campaign(db, current_user.id, campaign)


@router.get("/campaigns", response_model=List[MarketingCampaign])
def get_campaigns(
    status: Optional[str] = Query(None, description="Фильтр по статусу: draft, scheduled, published, archived"),
    platform: Optional[str] = Query(None, description="Фильтр по платформе: vk, telegram, instagram, facebook"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Получить список кампаний пользователя"""
    return MarketingService.get_campaigns(db, current_user.id, status, platform, skip, limit)


@router.get("/campaigns/{campaign_id}", response_model=MarketingCampaign)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Получить кампанию по ID"""
    campaign = MarketingService.get_campaign(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.put("/campaigns/{campaign_id}", response_model=MarketingCampaign)
def update_campaign(
    campaign_id: int,
    campaign_update: MarketingCampaignUpdate,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Обновить кампанию"""
    campaign = MarketingService.update_campaign(db, campaign_id, current_user.id, campaign_update)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.delete("/campaigns/{campaign_id}", status_code=204)
def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Удалить кампанию"""
    success = MarketingService.delete_campaign(db, campaign_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return None


# === AI Content Generation ===

@router.post("/generate-content", response_model=ContentGenerationResponse)
def generate_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Генерация контента с помощью AI
    
    Создаёт текст для поста/рекламы/новости на основе заданных параметров.
    В будущем будет интегрировано с Ollama/LiteLLM для реальной генерации.
    """
    return MarketingService.generate_content(request)


@router.post("/content-ideas", response_model=ContentIdeasResponse)
def get_content_ideas(
    request: ContentIdeasRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Получить идеи для контента
    
    AI предлагает несколько идей для постов на основе описания бизнеса.
    """
    return MarketingService.generate_content_ideas(request)


# === Analytics ===

@router.get("/campaigns/{campaign_id}/metrics", response_model=CampaignMetrics)
def get_campaign_metrics(
    campaign_id: int,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Получить метрики кампании (просмотры, лайки, шеры, вовлечённость)"""
    metrics = MarketingService.get_campaign_metrics(db, campaign_id, current_user.id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return metrics


@router.get("/statistics", response_model=CampaignStatistics)
def get_statistics(
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Получить общую статистику по всем кампаниям"""
    return MarketingService.get_statistics(db, current_user.id)


# === Content Calendar ===

@router.get("/calendar", response_model=ContentCalendar)
def get_content_calendar(
    month: int = Query(..., ge=1, le=12, description="Месяц (1-12)"),
    year: int = Query(..., ge=2020, le=2100, description="Год"),
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Получить календарь контента на указанный месяц"""
    return MarketingService.get_content_calendar(db, current_user.id, month, year)


# === Publishing ===

@router.post("/campaigns/{campaign_id}/publish", response_model=MarketingCampaign)
def publish_campaign(
    campaign_id: int,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """
    Опубликовать кампанию
    
    Изменяет статус на 'published' и устанавливает дату публикации.
    В будущем будет интегрировано с API социальных сетей.
    """
    campaign = MarketingService.publish_campaign(db, campaign_id, current_user.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign
