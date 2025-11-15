from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# ========== Template Schemas ==========

class TemplateBase(BaseModel):
    """Базовая схема шаблона"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    content: str = Field(..., min_length=1)
    category: Optional[str] = None
    document_type: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None


class TemplateCreate(TemplateBase):
    """Схема создания шаблона"""
    pass


class TemplateUpdate(BaseModel):
    """Схема обновления шаблона"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = None
    document_type: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None


class Template(TemplateBase):
    """Схема шаблона для ответа"""
    id: int
    is_system: bool
    user_id: Optional[int] = None
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TemplatePreview(BaseModel):
    """Краткая информация о шаблоне для списка"""
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    document_type: Optional[str] = None
    usage_count: int
    is_system: bool

    class Config:
        from_attributes = True


# ========== Document Schemas ==========

class DocumentBase(BaseModel):
    """Базовая схема документа"""
    title: str = Field(..., min_length=1, max_length=255)
    content: Optional[str] = None
    document_type: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    counterparty_name: Optional[str] = None
    counterparty_inn: Optional[str] = None
    amount: Optional[str] = None
    currency: str = "RUB"


class DocumentCreate(DocumentBase):
    """Схема создания документа"""
    template_id: Optional[int] = None


class DocumentUpdate(BaseModel):
    """Схема обновления документа"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    document_type: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern="^(draft|final|signed|archived)$")
    counterparty_name: Optional[str] = None
    counterparty_inn: Optional[str] = None
    amount: Optional[str] = None
    currency: Optional[str] = None


class Document(DocumentBase):
    """Схема документа для ответа"""
    id: int
    user_id: int
    template_id: Optional[int] = None
    file_path: Optional[str] = None
    file_format: str
    status: str
    version: int
    ai_generated: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentPreview(BaseModel):
    """Краткая информация о документе для списка"""
    id: int
    title: str
    document_type: Optional[str] = None
    status: str
    counterparty_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== Document Generation Schemas ==========

class GenerateDocumentRequest(BaseModel):
    """Запрос на генерацию документа из шаблона"""
    template_id: int
    title: str
    variables: Dict[str, Any]
    document_type: Optional[str] = None
    counterparty_name: Optional[str] = None
    counterparty_inn: Optional[str] = None
    amount: Optional[str] = None


class GenerateDocumentResponse(BaseModel):
    """Ответ после генерации документа"""
    document_id: int
    title: str
    content: str
    file_path: Optional[str] = None


class AIGenerateRequest(BaseModel):
    """Запрос на AI-генерацию текста документа"""
    document_type: str = Field(..., description="Тип документа: contract, act, invoice, etc.")
    purpose: str = Field(..., description="Назначение документа")
    parties: Dict[str, str] = Field(..., description="Стороны: {seller: ..., buyer: ...}")
    terms: Optional[Dict[str, Any]] = Field(None, description="Условия договора")
    additional_info: Optional[str] = Field(None, description="Дополнительная информация")


class AIGenerateResponse(BaseModel):
    """Ответ AI-генерации"""
    content: str
    suggested_title: str
    variables: Dict[str, Any]


# ========== Export Schemas ==========

class ExportDocumentRequest(BaseModel):
    """Запрос на экспорт документа"""
    document_id: int
    format: str = Field("pdf", pattern="^(pdf|docx|txt)$")


class ExportDocumentResponse(BaseModel):
    """Ответ после экспорта"""
    file_path: str
    file_name: str
    format: str
    size_bytes: int


# ========== Statistics Schemas ==========

class DocumentStatistics(BaseModel):
    """Статистика по документам"""
    total_documents: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    recent_documents: List[DocumentPreview]
    most_used_templates: List[TemplatePreview]
