from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date as date_type, datetime
from decimal import Decimal


# ========== FinanceRecord Schemas ==========

class FinanceRecordBase(BaseModel):
    """Базовая схема финансовой записи"""
    date: date_type
    description: Optional[str] = None
    amount: Decimal = Field(..., gt=0)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    type: str = Field(..., pattern="^(income|expense)$")
    counterparty: Optional[str] = None
    payment_method: Optional[str] = None
    account: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class FinanceRecordCreate(FinanceRecordBase):
    """Схема создания финансовой записи"""
    pass


class FinanceRecordUpdate(BaseModel):
    """Схема обновления финансовой записи"""
    date: Optional[date_type] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(income|expense)$")
    counterparty: Optional[str] = None
    payment_method: Optional[str] = None
    account: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    is_verified: Optional[bool] = None


class FinanceRecord(FinanceRecordBase):
    """Схема финансовой записи для ответа"""
    id: int
    user_id: int
    ai_category: Optional[str] = None
    ai_confidence: Optional[float] = None
    is_verified: bool
    source_file: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== CSV Upload Schemas ==========

class CSVUploadResponse(BaseModel):
    """Ответ после загрузки CSV"""
    success: bool
    records_created: int
    records_failed: int
    errors: List[str] = []
    file_name: str


class CSVRowData(BaseModel):
    """Данные одной строки CSV"""
    date: str
    description: str
    amount: str
    type: Optional[str] = None


# ========== Finance Summary Schemas ==========

class CategorySummary(BaseModel):
    """Сводка по категории"""
    category: str
    amount: Decimal
    count: int
    percentage: float


class FinanceSummary(BaseModel):
    """Финансовая сводка"""
    total_income: Decimal
    total_expense: Decimal
    net_income: Decimal
    transaction_count: int
    income_by_category: List[CategorySummary]
    expense_by_category: List[CategorySummary]
    period_start: date_type
    period_end: date_type


class MonthlyTrend(BaseModel):
    """Тренд по месяцам"""
    month: str
    income: Decimal
    expense: Decimal
    net: Decimal


class CashFlowData(BaseModel):
    """Данные денежного потока"""
    monthly_trends: List[MonthlyTrend]
    average_income: Decimal
    average_expense: Decimal
    highest_income_month: str
    highest_expense_month: str


# ========== Budget Schemas ==========

class FinanceBudgetBase(BaseModel):
    """Базовая схема бюджета"""
    category: str
    amount: Decimal = Field(..., gt=0)
    period: str = Field("monthly", pattern="^(monthly|yearly)$")
    start_date: date_type
    end_date: Optional[date_type] = None


class FinanceBudgetCreate(FinanceBudgetBase):
    """Схема создания бюджета"""
    pass


class FinanceBudgetUpdate(BaseModel):
    """Схема обновления бюджета"""
    amount: Optional[Decimal] = Field(None, gt=0)
    period: Optional[str] = Field(None, pattern="^(monthly|yearly)$")
    end_date: Optional[date_type] = None
    is_active: Optional[bool] = None


class FinanceBudget(FinanceBudgetBase):
    """Схема бюджета для ответа"""
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BudgetStatus(BaseModel):
    """Статус выполнения бюджета"""
    budget: FinanceBudget
    spent: Decimal
    remaining: Decimal
    percentage_used: float
    is_over_budget: bool


# ========== Goal Schemas ==========

class FinanceGoalBase(BaseModel):
    """Базовая схема финансовой цели"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    target_amount: Decimal = Field(..., gt=0)
    deadline: Optional[date_type] = None


class FinanceGoalCreate(FinanceGoalBase):
    """Схема создания финансовой цели"""
    pass


class FinanceGoalUpdate(BaseModel):
    """Схема обновления финансовой цели"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    target_amount: Optional[Decimal] = Field(None, gt=0)
    current_amount: Optional[Decimal] = Field(None, ge=0)
    deadline: Optional[date_type] = None
    status: Optional[str] = Field(None, pattern="^(active|completed|cancelled)$")


class FinanceGoal(FinanceGoalBase):
    """Схема финансовой цели для ответа"""
    id: int
    user_id: int
    current_amount: Decimal
    status: str
    progress_percentage: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @validator('progress_percentage', always=True)
    def calculate_progress(cls, v, values):
        """Рассчитать процент выполнения"""
        if 'target_amount' in values and 'current_amount' in values:
            target = float(values['target_amount'])
            current = float(values.get('current_amount', 0))
            if target > 0:
                return min((current / target) * 100, 100)
        return 0.0


# ========== AI Insights Schemas ==========

class AIInsight(BaseModel):
    """AI инсайт/рекомендация"""
    type: str  # warning, tip, opportunity
    title: str
    description: str
    priority: str  # high, medium, low
    category: Optional[str] = None
    amount: Optional[Decimal] = None


class FinanceInsights(BaseModel):
    """Набор AI инсайтов"""
    insights: List[AIInsight]
    generated_at: datetime
