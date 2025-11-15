from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


# === Base Schemas ===
class MarketingCampaignBase(BaseModel):
    """Базовая схема кампании"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    platform: Optional[str] = Field(None, description="vk, telegram, instagram, facebook")
    content_type: Optional[str] = Field(None, description="post, story, ad, newsletter")
    target_audience: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list, description="Хештеги и метки")
    scheduled_date: Optional[date] = None
    status: Optional[str] = Field("draft", description="draft, scheduled, published, archived")


class MarketingCampaignCreate(MarketingCampaignBase):
    """Создание кампании"""
    pass


class MarketingCampaignUpdate(BaseModel):
    """Обновление кампании"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = None
    platform: Optional[str] = None
    content_type: Optional[str] = None
    target_audience: Optional[str] = None
    tags: Optional[List[str]] = None
    scheduled_date: Optional[date] = None
    status: Optional[str] = None


class MarketingCampaignInDB(MarketingCampaignBase):
    """Кампания в БД"""
    id: int
    user_id: int
    ai_prompt: Optional[str] = None
    ai_generated: str = "false"
    published_date: Optional[datetime] = None
    views: int = 0
    likes: int = 0
    shares: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MarketingCampaign(MarketingCampaignInDB):
    """Полная схема кампании (для API)"""
    pass


# === AI Content Generation Schemas ===
class ContentGenerationRequest(BaseModel):
    """Запрос на генерацию контента"""
    title: str = Field(..., min_length=1, max_length=255)
    platform: str = Field(..., description="vk, telegram, instagram, facebook")
    content_type: str = Field(..., description="post, story, ad, newsletter")
    target_audience: Optional[str] = Field(None, description="Целевая аудитория")
    tone: Optional[str] = Field("professional", description="professional, casual, friendly, formal")
    keywords: Optional[List[str]] = Field(default_factory=list, description="Ключевые слова для включения")
    length: Optional[str] = Field("medium", description="short, medium, long")
    include_hashtags: bool = Field(True, description="Включить хештеги")
    include_emoji: bool = Field(True, description="Включить эмодзи")
    additional_instructions: Optional[str] = Field(None, description="Дополнительные инструкции для AI")


class ContentGenerationResponse(BaseModel):
    """Результат генерации контента"""
    content: str = Field(..., description="Сгенерированный текст")
    hashtags: Optional[List[str]] = Field(default_factory=list, description="Предложенные хештеги")
    suggested_title: Optional[str] = Field(None, description="Предложенный заголовок")
    ai_prompt: str = Field(..., description="Использованный промпт")


class ContentIdeasRequest(BaseModel):
    """Запрос идей для контента"""
    business_description: str = Field(..., description="Описание бизнеса")
    platform: str = Field(..., description="Платформа для публикации")
    count: int = Field(5, ge=1, le=20, description="Количество идей")


class ContentIdea(BaseModel):
    """Идея для контента"""
    title: str
    description: str
    content_type: str
    suggested_hashtags: List[str] = Field(default_factory=list)


class ContentIdeasResponse(BaseModel):
    """Список идей для контента"""
    ideas: List[ContentIdea]


# === Campaign Analytics Schemas ===
class CampaignMetrics(BaseModel):
    """Метрики кампании"""
    campaign_id: int
    views: int = 0
    likes: int = 0
    shares: int = 0
    engagement_rate: float = 0.0  # (likes + shares) / views * 100


class CampaignStatistics(BaseModel):
    """Статистика по всем кампаниям"""
    total_campaigns: int = 0
    draft_campaigns: int = 0
    scheduled_campaigns: int = 0
    published_campaigns: int = 0
    archived_campaigns: int = 0
    total_views: int = 0
    total_likes: int = 0
    total_shares: int = 0
    average_engagement_rate: float = 0.0
    campaigns_by_platform: dict = Field(default_factory=dict)


# === Platform-specific Schemas ===
class InstagramPostRequest(BaseModel):
    """Специфичный запрос для Instagram поста"""
    caption: str = Field(..., max_length=2200)
    hashtags: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    mentions: Optional[List[str]] = Field(default_factory=list)


class VKPostRequest(BaseModel):
    """Специфичный запрос для VK поста"""
    message: str
    attachments: Optional[List[str]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)


class TelegramPostRequest(BaseModel):
    """Специфичный запрос для Telegram поста"""
    text: str = Field(..., max_length=4096)
    parse_mode: Optional[str] = Field("Markdown", description="Markdown или HTML")
    disable_web_page_preview: bool = False


# === Calendar & Scheduling Schemas ===
class CalendarEntry(BaseModel):
    """Запись в календаре контента"""
    campaign_id: int
    title: str
    platform: str
    scheduled_date: date
    status: str


class ContentCalendar(BaseModel):
    """Календарь контента"""
    month: int
    year: int
    entries: List[CalendarEntry]
