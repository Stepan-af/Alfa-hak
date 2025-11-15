"""API endpoints для финансового модуля"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta

from app.database import get_db_sync
from app.auth import get_current_user
from app.models.user import User
from app.models.finance import FinanceRecord, FinanceBudget, FinanceGoal
from app.schemas.finance import (
    FinanceRecord as FinanceRecordSchema,
    FinanceRecordCreate,
    FinanceRecordUpdate,
    CSVUploadResponse,
    FinanceSummary,
    FinanceSummaryWithTrends,
    CashFlowData,
    FinanceInsights,
    FinanceBudget as FinanceBudgetSchema,
    FinanceBudgetCreate,
    FinanceBudgetUpdate,
    BudgetStatus,
    FinanceGoal as FinanceGoalSchema,
    FinanceGoalCreate,
    FinanceGoalUpdate,
)
from app.services.finance_service import FinanceService

router = APIRouter()


# ========== Транзакции ==========

@router.post("/records", response_model=FinanceRecordSchema, status_code=201)
async def create_record(
    record: FinanceRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Создать финансовую запись вручную"""
    
    # Автоматическая категоризация
    if not record.category:
        ai_category, ai_confidence = FinanceService.categorize_transaction(
            record.description or '',
            record.type
        )
        record.category = ai_category
    
    db_record = FinanceRecord(
        user_id=current_user.id,
        **record.model_dump()
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@router.get("/records", response_model=List[FinanceRecordSchema])
async def get_records(
    start_date: Optional[date] = Query(None, description="Начальная дата"),
    end_date: Optional[date] = Query(None, description="Конечная дата"),
    type: Optional[str] = Query(None, description="Тип: income или expense"),
    category: Optional[str] = Query(None, description="Категория"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить список финансовых записей с фильтрами"""
    
    query = db.query(FinanceRecord).filter(FinanceRecord.user_id == current_user.id)
    
    if start_date:
        query = query.filter(FinanceRecord.date >= start_date)
    if end_date:
        query = query.filter(FinanceRecord.date <= end_date)
    if type:
        query = query.filter(FinanceRecord.type == type)
    if category:
        query = query.filter(FinanceRecord.category == category)
    
    records = query.order_by(FinanceRecord.date.desc()).offset(offset).limit(limit).all()
    return records


@router.get("/records/{record_id}", response_model=FinanceRecordSchema)
async def get_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить одну финансовую запись"""
    
    record = db.query(FinanceRecord).filter(
        FinanceRecord.id == record_id,
        FinanceRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    return record


@router.put("/records/{record_id}", response_model=FinanceRecordSchema)
async def update_record(
    record_id: int,
    record_update: FinanceRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Обновить финансовую запись"""
    
    db_record = db.query(FinanceRecord).filter(
        FinanceRecord.id == record_id,
        FinanceRecord.user_id == current_user.id
    ).first()
    
    if not db_record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    # Обновление полей
    update_data = record_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record


@router.delete("/records/{record_id}", status_code=204)
async def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Удалить финансовую запись"""
    
    db_record = db.query(FinanceRecord).filter(
        FinanceRecord.id == record_id,
        FinanceRecord.user_id == current_user.id
    ).first()
    
    if not db_record:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    
    db.delete(db_record)
    db.commit()
    return None


# ========== CSV Upload ==========

@router.post("/upload-csv", response_model=CSVUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """
    Загрузить финансовые данные из CSV файла
    
    Ожидаемые колонки (гибкий парсинг):
    - date / Дата (DD.MM.YYYY или YYYY-MM-DD)
    - description / Описание / Назначение
    - amount / Сумма (число, может быть с минусом)
    - type / Тип (опционально: income/expense, доход/расход, +/-)
    - category / Категория (опционально)
    - counterparty / Контрагент (опционально)
    """
    
    # Проверка типа файла
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Файл должен быть в формате CSV")
    
    # Чтение содержимого
    content = await file.read()
    
    # Попытка определить кодировку
    encodings = ['utf-8', 'windows-1251', 'cp1251']
    result = None
    
    for encoding in encodings:
        try:
            result = await FinanceService.upload_csv(
                db=db,
                user_id=current_user.id,
                file_content=content,
                file_name=file.filename,
                encoding=encoding
            )
            if result.success:
                break
        except UnicodeDecodeError:
            continue
    
    if not result or not result.success:
        raise HTTPException(
            status_code=400,
            detail="Не удалось обработать файл. Проверьте формат и кодировку."
        )
    
    return result


# ========== Аналитика ==========

@router.get("/summary", response_model=FinanceSummary)
async def get_summary(
    start_date: Optional[date] = Query(None, description="Начальная дата (по умолчанию: начало текущего месяца)"),
    end_date: Optional[date] = Query(None, description="Конечная дата (по умолчанию: сегодня)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить финансовую сводку за период"""
    
    return FinanceService.get_summary(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/summary-with-trends", response_model=FinanceSummaryWithTrends)
async def get_summary_with_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить финансовую сводку с трендами (сравнение с предыдущим периодом)"""
    from datetime import datetime
    from decimal import Decimal
    
    # Текущий период: текущий месяц
    today = date.today()
    current_start = date(today.year, today.month, 1)
    current_end = today
    
    # Предыдущий период: предыдущий месяц
    if today.month == 1:
        prev_start = date(today.year - 1, 12, 1)
        prev_end = date(today.year - 1, 12, 31)
    else:
        prev_start = date(today.year, today.month - 1, 1)
        # Последний день предыдущего месяца
        prev_end = current_start - timedelta(days=1)
    
    # Получаем данные за оба периода
    current_summary = FinanceService.get_summary(
        db=db,
        user_id=current_user.id,
        start_date=current_start,
        end_date=current_end
    )
    
    previous_summary = FinanceService.get_summary(
        db=db,
        user_id=current_user.id,
        start_date=prev_start,
        end_date=prev_end
    )
    
    # Функция для расчёта тренда
    def calculate_trend(current: Decimal, previous: Decimal) -> dict:
        change_absolute = current - previous
        
        if previous == 0:
            change_percent = 100.0 if current > 0 else 0.0
        else:
            change_percent = float((change_absolute / previous) * 100)
        
        if change_percent > 0.5:
            direction = "up"
        elif change_percent < -0.5:
            direction = "down"
        else:
            direction = "neutral"
        
        return {
            "current_value": current,
            "previous_value": previous,
            "change_percent": round(change_percent, 1),
            "change_absolute": change_absolute,
            "direction": direction
        }
    
    # Рассчитываем тренды
    return {
        "total_income": calculate_trend(
            current_summary.total_income,
            previous_summary.total_income
        ),
        "total_expense": calculate_trend(
            current_summary.total_expense,
            previous_summary.total_expense
        ),
        "net_income": calculate_trend(
            current_summary.net_income,
            previous_summary.net_income
        ),
        "transaction_count": {
            "current": current_summary.transaction_count,
            "previous": previous_summary.transaction_count,
            "change": current_summary.transaction_count - previous_summary.transaction_count
        },
        "current_period": current_summary,
        "previous_period": previous_summary
    }


@router.get("/cash-flow", response_model=CashFlowData)
async def get_cash_flow(
    months: int = Query(12, ge=1, le=24, description="Количество месяцев для анализа"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить данные денежного потока по месяцам"""
    
    return FinanceService.get_cash_flow(
        db=db,
        user_id=current_user.id,
        months=months
    )


@router.get("/insights", response_model=FinanceInsights)
async def get_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить AI-инсайты и рекомендации по финансам"""
    
    return FinanceService.generate_insights(
        db=db,
        user_id=current_user.id
    )


@router.get("/categories", response_model=List[str])
async def get_categories(
    type: str = Query(..., description="Тип: income или expense"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить список уникальных категорий пользователя"""
    
    categories = db.query(FinanceRecord.category).filter(
        FinanceRecord.user_id == current_user.id,
        FinanceRecord.type == type,
        FinanceRecord.category.isnot(None)
    ).distinct().all()
    
    return [cat[0] for cat in categories if cat[0]]


# ========== Бюджеты ==========

@router.post("/budgets", response_model=FinanceBudgetSchema, status_code=201)
async def create_budget(
    budget: FinanceBudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Создать бюджет по категории"""
    
    return FinanceService.create_budget(
        db=db,
        user_id=current_user.id,
        budget=budget
    )


@router.get("/budgets", response_model=List[FinanceBudgetSchema])
async def get_budgets(
    active_only: bool = Query(True, description="Показать только активные бюджеты"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить список бюджетов"""
    
    query = db.query(FinanceBudget).filter(FinanceBudget.user_id == current_user.id)
    
    if active_only:
        query = query.filter(FinanceBudget.is_active == True)
    
    budgets = query.order_by(FinanceBudget.created_at.desc()).all()
    return budgets


@router.get("/budgets/{budget_id}/status", response_model=BudgetStatus)
async def get_budget_status(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить статус выполнения бюджета"""
    
    status = FinanceService.get_budget_status(
        db=db,
        budget_id=budget_id,
        user_id=current_user.id
    )
    
    if not status:
        raise HTTPException(status_code=404, detail="Бюджет не найден")
    
    return status


@router.put("/budgets/{budget_id}", response_model=FinanceBudgetSchema)
async def update_budget(
    budget_id: int,
    budget_update: FinanceBudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Обновить бюджет"""
    
    db_budget = db.query(FinanceBudget).filter(
        FinanceBudget.id == budget_id,
        FinanceBudget.user_id == current_user.id
    ).first()
    
    if not db_budget:
        raise HTTPException(status_code=404, detail="Бюджет не найден")
    
    update_data = budget_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_budget, field, value)
    
    db.commit()
    db.refresh(db_budget)
    return db_budget


# ========== Финансовые цели ==========

@router.post("/goals", response_model=FinanceGoalSchema, status_code=201)
async def create_goal(
    goal: FinanceGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Создать финансовую цель"""
    
    return FinanceService.create_goal(
        db=db,
        user_id=current_user.id,
        goal=goal
    )


@router.get("/goals", response_model=List[FinanceGoalSchema])
async def get_goals(
    status: Optional[str] = Query(None, description="Фильтр по статусу: active, completed, cancelled"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Получить список финансовых целей"""
    
    query = db.query(FinanceGoal).filter(FinanceGoal.user_id == current_user.id)
    
    if status:
        query = query.filter(FinanceGoal.status == status)
    
    goals = query.order_by(FinanceGoal.created_at.desc()).all()
    return goals


@router.put("/goals/{goal_id}", response_model=FinanceGoalSchema)
async def update_goal(
    goal_id: int,
    goal_update: FinanceGoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Обновить финансовую цель"""
    
    db_goal = db.query(FinanceGoal).filter(
        FinanceGoal.id == goal_id,
        FinanceGoal.user_id == current_user.id
    ).first()
    
    if not db_goal:
        raise HTTPException(status_code=404, detail="Цель не найдена")
    
    update_data = goal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_goal, field, value)
    
    db.commit()
    db.refresh(db_goal)
    return db_goal
