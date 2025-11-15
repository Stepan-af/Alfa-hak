from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Task(Base):
    """Задача пользователя"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Приоритет и статус
    priority = Column(String(20), default="medium", index=True)  # low, medium, high, urgent
    status = Column(String(50), default="todo", index=True)  # todo, in_progress, done, cancelled
    
    # Даты
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    reminder_at = Column(DateTime(timezone=True), nullable=True)
    
    # Категория и теги
    category = Column(String(100), nullable=True, index=True)
    tags = Column(JSON, nullable=True)  # Список тегов
    
    # AI и автоматизация
    ai_suggested = Column(Boolean, default=False)  # Предложено AI
    ai_context = Column(Text, nullable=True)  # Контекст для AI
    
    # Повторяющиеся задачи
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(100), nullable=True)  # daily, weekly, monthly
    parent_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    
    # Вложения и ссылки
    attachments = Column(JSON, nullable=True)  # Список файлов/ссылок
    linked_document_id = Column(Integer, nullable=True)  # Ссылка на документ
    
    # Оценка времени
    estimated_minutes = Column(Integer, nullable=True)
    actual_minutes = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    subtasks = relationship("Task", backref="parent_task", remote_side=[id], cascade="all")
    
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_user_priority', 'user_id', 'priority'),
        Index('idx_user_due_date', 'user_id', 'due_date'),
        Index('idx_user_category', 'user_id', 'category'),
    )
