from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Document(Base):
    """Документ пользователя"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True, index=True)
    
    # Метаданные документа
    document_type = Column(String(100), nullable=True)  # contract, act, invoice, agreement
    variables = Column(JSON, nullable=True)  # Переменные для подстановки
    file_path = Column(String(500), nullable=True)
    file_format = Column(String(20), default="docx")  # docx, pdf, txt
    
    # Статус и версионирование
    status = Column(String(50), default="draft")  # draft, final, signed, archived
    version = Column(Integer, default=1)
    
    # Связь с контрагентами/клиентами
    counterparty_name = Column(String(255), nullable=True)
    counterparty_inn = Column(String(50), nullable=True)
    
    # Финансовая информация
    amount = Column(String(100), nullable=True)
    currency = Column(String(10), default="RUB")
    
    # AI-функции
    ai_generated = Column(String(50), nullable=True)  # Какая часть сгенерирована AI
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="documents")
    template = relationship("Template", back_populates="documents")
    
    __table_args__ = (
        Index('idx_user_type', 'user_id', 'document_type'),
        Index('idx_user_status', 'user_id', 'status'),
    )


class Template(Base):
    """Шаблон документа"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    
    # Категория и тип
    category = Column(String(100), nullable=True, index=True)  # legal, finance, hr
    document_type = Column(String(100), nullable=True)  # contract, act, invoice
    
    # Переменные шаблона
    variables = Column(JSON, nullable=True)  # Список переменных: {var_name: {type, required, default}}
    
    # Системный или пользовательский
    is_system = Column(String(10), default="false")  # Системные шаблоны доступны всем
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    
    # Популярность
    usage_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="templates")
    documents = relationship("Document", back_populates="template", cascade="all, delete-orphan")
