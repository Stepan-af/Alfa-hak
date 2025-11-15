"""API endpoints для модуля документов"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db_sync
from app.auth import get_current_user
from app.models.user import User
from app.models.document import Document, Template
from app.schemas.document import (
    Document as DocumentSchema,
    DocumentCreate,
    DocumentUpdate,
    DocumentPreview,
    Template as TemplateSchema,
    TemplateCreate,
    TemplateUpdate,
    TemplatePreview,
    GenerateDocumentRequest,
    GenerateDocumentResponse,
    AIGenerateRequest,
    AIGenerateResponse,
    DocumentStatistics,
)
from app.services.document_service import DocumentService

router = APIRouter()


# ========== Templates ==========

@router.get("/templates", response_model=List[TemplatePreview])
async def get_templates(
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    document_type: Optional[str] = Query(None, description="Фильтр по типу документа"),
    include_user: bool = Query(True, description="Включать пользовательские шаблоны"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить список шаблонов"""
    
    query = db.query(Template)
    
    # Системные шаблоны доступны всем
    if include_user:
        query = query.filter(
            (Template.is_system == "true") | (Template.user_id == current_user.id)
        )
    else:
        query = query.filter(Template.is_system == "true")
    
    if category:
        query = query.filter(Template.category == category)
    if document_type:
        query = query.filter(Template.document_type == document_type)
    
    templates = query.order_by(Template.usage_count.desc()).all()
    return templates


@router.get("/templates/{template_id}", response_model=TemplateSchema)
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить детали шаблона"""
    
    template = db.query(Template).filter(Template.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    
    # Проверка доступа
    if template.is_system != "true" and template.user_id != current_user.id:  # type: ignore
        raise HTTPException(status_code=403, detail="Нет доступа к этому шаблону")
    
    return template


@router.post("/templates", response_model=TemplateSchema, status_code=201)
async def create_template(
    template: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Создать пользовательский шаблон"""
    
    db_template = Template(
        user_id=current_user.id,
        is_system="false",
        **template.model_dump()
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.put("/templates/{template_id}", response_model=TemplateSchema)
async def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Обновить пользовательский шаблон"""
    
    db_template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()
    
    if not db_template:
        raise HTTPException(status_code=404, detail="Шаблон не найден или нет доступа")
    
    update_data = template_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Удалить пользовательский шаблон"""
    
    db_template = db.query(Template).filter(
        Template.id == template_id,
        Template.user_id == current_user.id
    ).first()
    
    if not db_template:
        raise HTTPException(status_code=404, detail="Шаблон не найден или нет доступа")
    
    db.delete(db_template)
    db.commit()
    return None


# ========== Documents ==========

@router.get("/", response_model=List[DocumentPreview])
async def get_documents(
    document_type: Optional[str] = Query(None, description="Фильтр по типу"),
    status: Optional[str] = Query(None, description="Фильтр по статусу"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить список документов пользователя"""
    
    query = db.query(Document).filter(Document.user_id == current_user.id)
    
    if document_type:
        query = query.filter(Document.document_type == document_type)
    if status:
        query = query.filter(Document.status == status)
    
    documents = query.order_by(Document.created_at.desc()).offset(offset).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить детали документа"""
    
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    return document


@router.post("/", response_model=DocumentSchema, status_code=201)
async def create_document(
    document: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Создать документ вручную"""
    
    db_document = Document(
        user_id=current_user.id,
        **document.model_dump()
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.put("/{document_id}", response_model=DocumentSchema)
async def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Обновить документ"""
    
    db_document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not db_document:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    update_data = document_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_document, field, value)
    
    # Увеличиваем версию при изменении контента
    if 'content' in update_data:
        db_document.version += 1  # type: ignore
    
    db.commit()
    db.refresh(db_document)
    return db_document


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Удалить документ"""
    
    db_document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not db_document:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    db.delete(db_document)
    db.commit()
    return None


# ========== Document Generation ==========

@router.post("/generate", response_model=GenerateDocumentResponse, status_code=201)
async def generate_document(
    request: GenerateDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Сгенерировать документ из шаблона"""
    
    try:
        document = await DocumentService.generate_document(
            db=db,
            user_id=int(current_user.id),  # type: ignore
            request=request
        )
        
        return GenerateDocumentResponse(
            document_id=int(document.id),  # type: ignore
            title=str(document.title),  # type: ignore
            content=str(document.content or ""),  # type: ignore
            file_path=str(document.file_path) if document.file_path else None  # type: ignore
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ai-generate", response_model=AIGenerateResponse)
async def ai_generate_document(
    request: AIGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """AI-генерация текста документа"""
    
    result = await DocumentService.ai_generate_document(request)
    
    return AIGenerateResponse(
        content=result["content"],
        suggested_title=result["suggested_title"],
        variables=result["variables"]
    )


# ========== Statistics ==========

@router.get("/stats/summary", response_model=DocumentStatistics)
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить статистику по документам"""
    
    stats = DocumentService.get_statistics(db, int(current_user.id))  # type: ignore
    return stats


# ========== Initialization ==========

@router.post("/init-templates", status_code=201)
async def initialize_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Инициализация системных шаблонов (только для первого запуска)"""
    
    created = DocumentService.create_system_templates(db)
    return {"created": created, "message": f"Создано {created} системных шаблонов"}
