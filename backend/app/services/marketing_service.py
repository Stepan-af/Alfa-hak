from typing import List, Optional, Dict
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.models.marketing import MarketingCampaign
from app.schemas.marketing import (
    MarketingCampaignCreate,
    MarketingCampaignUpdate,
    ContentGenerationRequest,
    ContentGenerationResponse,
    ContentIdeasRequest,
    ContentIdea,
    ContentIdeasResponse,
    CampaignMetrics,
    CampaignStatistics,
    CalendarEntry,
    ContentCalendar,
)


class MarketingService:
    """Сервис для работы с маркетинговыми кампаниями"""

    # === CRUD Operations ===
    
    @staticmethod
    def create_campaign(db: Session, user_id: int, campaign: MarketingCampaignCreate) -> MarketingCampaign:
        """Создать новую кампанию"""
        db_campaign = MarketingCampaign(
            user_id=user_id,
            **campaign.model_dump()
        )
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        return db_campaign

    @staticmethod
    def get_campaigns(
        db: Session,
        user_id: int,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MarketingCampaign]:
        """Получить список кампаний"""
        query = db.query(MarketingCampaign).filter(MarketingCampaign.user_id == user_id)
        
        if status:
            query = query.filter(MarketingCampaign.status == status)
        if platform:
            query = query.filter(MarketingCampaign.platform == platform)
        
        return query.order_by(MarketingCampaign.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_campaign(db: Session, campaign_id: int, user_id: int) -> Optional[MarketingCampaign]:
        """Получить кампанию по ID"""
        return db.query(MarketingCampaign).filter(
            MarketingCampaign.id == campaign_id,
            MarketingCampaign.user_id == user_id
        ).first()

    @staticmethod
    def update_campaign(
        db: Session,
        campaign_id: int,
        user_id: int,
        campaign_update: MarketingCampaignUpdate
    ) -> Optional[MarketingCampaign]:
        """Обновить кампанию"""
        db_campaign = MarketingService.get_campaign(db, campaign_id, user_id)
        if not db_campaign:
            return None
        
        update_data = campaign_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_campaign, field, value)
        
        db.commit()
        db.refresh(db_campaign)
        return db_campaign

    @staticmethod
    def delete_campaign(db: Session, campaign_id: int, user_id: int) -> bool:
        """Удалить кампанию"""
        db_campaign = MarketingService.get_campaign(db, campaign_id, user_id)
        if not db_campaign:
            return False
        
        db.delete(db_campaign)
        db.commit()
        return True

    # === AI Content Generation ===

    @staticmethod
    def generate_content(request: ContentGenerationRequest) -> ContentGenerationResponse:
        """
        Генерация контента с помощью AI
        TODO: Интеграция с Ollama/LiteLLM для реальной генерации
        """
        # Построение промпта
        prompt = MarketingService._build_generation_prompt(request)
        
        # TODO: Вызов LLM API (Ollama/LiteLLM)
        # Пока возвращаем шаблонный контент
        generated_content = MarketingService._generate_mock_content(request)
        hashtags = MarketingService._generate_hashtags(request)
        
        return ContentGenerationResponse(
            content=generated_content,
            hashtags=hashtags,
            suggested_title=request.title,
            ai_prompt=prompt
        )

    @staticmethod
    def _build_generation_prompt(request: ContentGenerationRequest) -> str:
        """Построить промпт для AI"""
        prompt_parts = [
            f"Создай {request.content_type} для {request.platform}.",
            f"Тема: {request.title}",
        ]
        
        if request.target_audience:
            prompt_parts.append(f"Целевая аудитория: {request.target_audience}")
        
        prompt_parts.append(f"Тон: {request.tone}")
        prompt_parts.append(f"Длина: {request.length}")
        
        if request.keywords:
            prompt_parts.append(f"Ключевые слова: {', '.join(request.keywords)}")
        
        if request.include_hashtags:
            prompt_parts.append("Включи релевантные хештеги.")
        
        if request.include_emoji:
            prompt_parts.append("Используй эмодзи для большей вовлечённости.")
        
        if request.additional_instructions:
            prompt_parts.append(f"Дополнительно: {request.additional_instructions}")
        
        return " ".join(prompt_parts)

    @staticmethod
    def _generate_mock_content(request: ContentGenerationRequest) -> str:
        """Сгенерировать тестовый контент"""
        platform_templates = {
            "instagram": "✨ {title}\n\n📸 {description}\n\n{call_to_action}",
            "vk": "{title}\n\n{description}\n\n{call_to_action}",
            "telegram": "📢 <b>{title}</b>\n\n{description}\n\n{call_to_action}",
            "facebook": "{title}\n\n{description}\n\nУзнать больше: {call_to_action}",
        }
        
        template = platform_templates.get(request.platform.lower(), "{title}\n\n{description}")
        
        description = (
            f"Мы рады представить вам новое предложение! "
            f"Это отличная возможность для {request.target_audience or 'нашей аудитории'}."
        )
        
        cta = "Свяжитесь с нами для подробностей!"
        
        content = template.format(
            title=request.title,
            description=description,
            call_to_action=cta
        )
        
        if request.include_emoji and request.platform.lower() not in ["telegram"]:
            content += " 🚀💼✨"
        
        return content

    @staticmethod
    def _generate_hashtags(request: ContentGenerationRequest) -> List[str]:
        """Сгенерировать хештеги"""
        hashtags = []
        
        # Базовые хештеги из ключевых слов
        if request.keywords:
            hashtags.extend([f"#{kw.replace(' ', '')}" for kw in request.keywords[:5]])
        
        # Добавить популярные хештеги по платформе
        platform_hashtags = {
            "instagram": ["#бизнес", "#маркетинг", "#продвижение"],
            "vk": ["#бизнес", "#реклама", "#маркетинг"],
            "facebook": ["#business", "#marketing", "#advertising"],
            "telegram": [],  # В Telegram хештеги менее важны
        }
        
        if request.platform.lower() in platform_hashtags:
            hashtags.extend(platform_hashtags[request.platform.lower()])
        
        return hashtags[:10]  # Ограничить 10 хештегами

    @staticmethod
    def generate_content_ideas(request: ContentIdeasRequest) -> ContentIdeasResponse:
        """
        Генерация идей для контента
        TODO: Интеграция с LLM для реальной генерации
        """
        # Шаблонные идеи (заменить на AI генерацию)
        ideas_templates = [
            {
                "title": "История успеха клиента",
                "description": "Поделитесь кейсом довольного клиента с результатами",
                "content_type": "post",
                "hashtags": ["#успех", "#клиент", "#результат"]
            },
            {
                "title": "Советы от экспертов",
                "description": "5 практических советов для вашей аудитории",
                "content_type": "post",
                "hashtags": ["#советы", "#эксперт", "#полезное"]
            },
            {
                "title": "За кулисами",
                "description": "Покажите процесс работы вашей команды",
                "content_type": "story",
                "hashtags": ["#команда", "#процесс", "#работа"]
            },
            {
                "title": "Новый продукт/услуга",
                "description": "Анонс нового предложения с акцентом на выгоды",
                "content_type": "ad",
                "hashtags": ["#новинка", "#акция", "#специальноепредложение"]
            },
            {
                "title": "Опрос аудитории",
                "description": "Узнайте мнение подписчиков по важной теме",
                "content_type": "post",
                "hashtags": ["#опрос", "#мнение", "#обратнаясвязь"]
            },
        ]
        
        ideas = [
            ContentIdea(
                title=idea["title"],
                description=f"{idea['description']} - {request.business_description}",
                content_type=idea["content_type"],
                suggested_hashtags=idea["hashtags"]
            )
            for idea in ideas_templates[:request.count]
        ]
        
        return ContentIdeasResponse(ideas=ideas)

    # === Analytics & Statistics ===

    @staticmethod
    def get_campaign_metrics(db: Session, campaign_id: int, user_id: int) -> Optional[CampaignMetrics]:
        """Получить метрики кампании"""
        campaign = MarketingService.get_campaign(db, campaign_id, user_id)
        if not campaign:
            return None
        
        engagement_rate = 0.0
        campaign_views = int(campaign.views)  # type: ignore
        if campaign_views > 0:  # type: ignore
            engagement_rate = ((int(campaign.likes) + int(campaign.shares)) / campaign_views) * 100  # type: ignore
        
        return CampaignMetrics(
            campaign_id=int(campaign.id),  # type: ignore
            views=int(campaign.views),  # type: ignore
            likes=int(campaign.likes),  # type: ignore
            shares=int(campaign.shares),  # type: ignore
            engagement_rate=round(float(engagement_rate), 2)  # type: ignore
        )

    @staticmethod
    def get_statistics(db: Session, user_id: int) -> CampaignStatistics:
        """Получить общую статистику по кампаниям"""
        campaigns = db.query(MarketingCampaign).filter(MarketingCampaign.user_id == user_id).all()
        
        total = len(campaigns)
        draft = sum(1 for c in campaigns if str(c.status) == "draft")  # type: ignore
        scheduled = sum(1 for c in campaigns if str(c.status) == "scheduled")  # type: ignore
        published = sum(1 for c in campaigns if str(c.status) == "published")  # type: ignore
        archived = sum(1 for c in campaigns if str(c.status) == "archived")  # type: ignore
        
        total_views = sum(int(c.views) for c in campaigns)  # type: ignore
        total_likes = sum(int(c.likes) for c in campaigns)  # type: ignore
        total_shares = sum(int(c.shares) for c in campaigns)  # type: ignore
        
        avg_engagement = 0.0
        if total_views > 0:  # type: ignore
            avg_engagement = ((total_likes + total_shares) / total_views) * 100
        
        # Группировка по платформам
        platforms: Dict[str, int] = {}
        for campaign in campaigns:
            platform_str = str(campaign.platform) if campaign.platform else None  # type: ignore
            if platform_str:  # type: ignore
                platforms[platform_str] = platforms.get(platform_str, 0) + 1  # type: ignore
        
        return CampaignStatistics(
            total_campaigns=total,
            draft_campaigns=draft,
            scheduled_campaigns=scheduled,
            published_campaigns=published,
            archived_campaigns=archived,
            total_views=int(total_views),  # type: ignore
            total_likes=int(total_likes),  # type: ignore
            total_shares=int(total_shares),  # type: ignore
            average_engagement_rate=round(float(avg_engagement), 2),  # type: ignore
            campaigns_by_platform=platforms
        )

    # === Content Calendar ===

    @staticmethod
    def get_content_calendar(db: Session, user_id: int, month: int, year: int) -> ContentCalendar:
        """Получить календарь контента на месяц"""
        # Фильтр по месяцу и году
        campaigns = db.query(MarketingCampaign).filter(
            MarketingCampaign.user_id == user_id,
            MarketingCampaign.scheduled_date.isnot(None),
            extract('month', MarketingCampaign.scheduled_date) == month,
            extract('year', MarketingCampaign.scheduled_date) == year
        ).order_by(MarketingCampaign.scheduled_date).all()
        
        entries = [
            CalendarEntry(
                campaign_id=int(c.id),  # type: ignore
                title=str(c.title),  # type: ignore
                platform=str(c.platform) if c.platform else "unknown",  # type: ignore
                scheduled_date=c.scheduled_date,  # type: ignore
                status=str(c.status)  # type: ignore
            )
            for c in campaigns
        ]
        
        return ContentCalendar(month=month, year=year, entries=entries)

    # === Publishing ===

    @staticmethod
    def publish_campaign(db: Session, campaign_id: int, user_id: int) -> Optional[MarketingCampaign]:
        """
        Опубликовать кампанию
        TODO: Интеграция с API платформ (VK, Telegram, etc.)
        """
        campaign = MarketingService.get_campaign(db, campaign_id, user_id)
        if not campaign:
            return None
        
        # Обновить статус и дату публикации
        campaign.status = "published"  # type: ignore
        campaign.published_date = datetime.utcnow()  # type: ignore
        
        db.commit()
        db.refresh(campaign)
        
        # TODO: Реальная публикация на платформу
        # - Вызов API VK, Telegram Bot API, Instagram Graph API
        # - Обработка ошибок и ретраи
        
        return campaign
