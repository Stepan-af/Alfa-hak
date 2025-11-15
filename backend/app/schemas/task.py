from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# === Base Schemas ===
class TaskBase(BaseModel):
    """Базовая схема задачи"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = Field("medium", description="low, medium, high, urgent")
    status: Optional[str] = Field("todo", description="todo, in_progress, done, cancelled")
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    estimated_minutes: Optional[int] = Field(None, ge=0)


class TaskCreate(TaskBase):
    """Создание задачи"""
    pass


class TaskUpdate(BaseModel):
    """Обновление задачи"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    estimated_minutes: Optional[int] = Field(None, ge=0)
    actual_minutes: Optional[int] = Field(None, ge=0)


class TaskInDB(TaskBase):
    """Задача в БД"""
    id: int
    user_id: int
    completed_at: Optional[datetime] = None
    ai_suggested: bool = False
    ai_context: Optional[str] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    parent_task_id: Optional[int] = None
    attachments: Optional[List[dict]] = None
    linked_document_id: Optional[int] = None
    actual_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Task(TaskInDB):
    """Полная схема задачи (для API)"""
    subtasks: Optional[List["Task"]] = Field(default_factory=list)


# === AI Suggestions ===
class TaskSuggestionRequest(BaseModel):
    """Запрос на AI предложения задач"""
    context: str = Field(..., description="Контекст бизнеса/проекта")
    count: int = Field(5, ge=1, le=20)
    priority: Optional[str] = None
    category: Optional[str] = None


class TaskSuggestion(BaseModel):
    """Предложенная задача от AI"""
    title: str
    description: str
    priority: str
    category: str
    estimated_minutes: Optional[int] = None
    tags: List[str] = Field(default_factory=list)


class TaskSuggestionsResponse(BaseModel):
    """Список предложенных задач"""
    suggestions: List[TaskSuggestion]


# === Smart Scheduling ===
class SmartScheduleRequest(BaseModel):
    """Запрос на умное планирование"""
    tasks: List[int] = Field(..., description="ID задач для планирования")
    work_hours_per_day: int = Field(8, ge=1, le=16)
    start_date: Optional[datetime] = None


class ScheduledTask(BaseModel):
    """Запланированная задача"""
    task_id: int
    suggested_date: datetime
    rationale: str


class SmartScheduleResponse(BaseModel):
    """Результат планирования"""
    scheduled_tasks: List[ScheduledTask]


# === Recurring Tasks ===
class RecurringTaskCreate(TaskCreate):
    """Создание повторяющейся задачи"""
    recurrence_pattern: str = Field(..., description="daily, weekly, monthly, yearly")
    recurrence_end_date: Optional[datetime] = None


# === Statistics ===
class TaskStatistics(BaseModel):
    """Статистика по задачам"""
    total_tasks: int = 0
    todo_tasks: int = 0
    in_progress_tasks: int = 0
    done_tasks: int = 0
    cancelled_tasks: int = 0
    overdue_tasks: int = 0
    today_tasks: int = 0
    this_week_tasks: int = 0
    high_priority_tasks: int = 0
    urgent_priority_tasks: int = 0
    completion_rate: float = 0.0  # Процент выполненных
    average_completion_minutes: Optional[float] = None
    tasks_by_category: dict = Field(default_factory=dict)
    tasks_by_priority: dict = Field(default_factory=dict)


# === Task Filters ===
class TaskFilter(BaseModel):
    """Фильтры для задач"""
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    is_overdue: Optional[bool] = None
    has_subtasks: Optional[bool] = None
    search_query: Optional[str] = None


# === Bulk Operations ===
class BulkUpdateTasksRequest(BaseModel):
    """Массовое обновление задач"""
    task_ids: List[int] = Field(..., min_length=1)
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None


class BulkDeleteTasksRequest(BaseModel):
    """Массовое удаление задач"""
    task_ids: List[int] = Field(..., min_length=1)


# === Task Templates ===
class TaskTemplate(BaseModel):
    """Шаблон задачи"""
    name: str
    tasks: List[TaskCreate]


# === Productivity Insights ===
class ProductivityInsight(BaseModel):
    """Инсайт по продуктивности"""
    type: str  # "warning", "tip", "achievement"
    title: str
    message: str
    action: Optional[str] = None


class ProductivityReport(BaseModel):
    """Отчёт по продуктивности"""
    period: str  # "today", "this_week", "this_month"
    completed_tasks: int
    total_time_minutes: int
    most_productive_category: Optional[str] = None
    insights: List[ProductivityInsight] = Field(default_factory=list)


# Update forward references
Task.model_rebuild()
