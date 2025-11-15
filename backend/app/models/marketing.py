from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class MarketingCampaign(Base):
    """Маркетинговая кампания"""
    __tablename__ = "marketing_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    
    # Платформа и тип контента
    platform = Column(String(100), nullable=True, index=True)  # vk, telegram, instagram, facebook
    content_type = Column(String(100), nullable=True)  # post, story, ad, newsletter
    
    # Целевая аудитория
    target_audience = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)  # Хештеги и метки
    
    # Планирование
    scheduled_date = Column(Date, nullable=True)
    published_date = Column(DateTime(timezone=True), nullable=True)
    
    # Статус
    status = Column(String(50), default="draft", index=True)  # draft, scheduled, published, archived
    
    # AI генерация
    ai_prompt = Column(Text, nullable=True)  # Промпт для AI
    ai_generated = Column(String(10), default="false")  # Был ли контент сгенерирован AI
    
    # Метрики (для будущего)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="marketing_campaigns")
    
    __table_args__ = (
        Index('idx_user_platform', 'user_id', 'platform'),
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_scheduled_date', 'scheduled_date'),
    )
