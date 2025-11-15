from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db_sync
from app.auth import get_current_user
from app.models.user import User
from app.schemas.task import (
    Task,
    TaskCreate,
    TaskUpdate,
    TaskSuggestionRequest,
    TaskSuggestionsResponse,
    TaskStatistics,
    ProductivityReport,
    BulkUpdateTasksRequest,
    BulkDeleteTasksRequest,
)
from app.services.task_service import TaskService

router = APIRouter()


# === Task CRUD ===

@router.post("/tasks", response_model=Task, status_code=201)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Создать новую задачу"""
    return TaskService.create_task(db, current_user.id, task)


@router.get("/tasks", response_model=List[Task])
def get_tasks(
    status: Optional[str] = Query(None, description="Фильтр по статусу: todo, in_progress, done, cancelled"),
    priority: Optional[str] = Query(None, description="Фильтр по приоритету: low, medium, high, urgent"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    is_overdue: Optional[bool] = Query(None, description="Показать только просроченные"),
    search: Optional[str] = Query(None, description="Поиск по названию и описанию"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Получить список задач пользователя с фильтрами"""
    return TaskService.get_tasks(
        db, current_user.id, status, priority, category, is_overdue, search, skip, limit
    )


@router.get("/tasks/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Получить задачу по ID"""
    task = TaskService.get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Обновить задачу"""
    task = TaskService.update_task(db, task_id, current_user.id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Удалить задачу"""
    success = TaskService.delete_task(db, task_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None


# === Bulk Operations ===

@router.post("/tasks/bulk-update")
def bulk_update_tasks(
    request: BulkUpdateTasksRequest,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Массовое обновление задач"""
    count = TaskService.bulk_update_tasks(
        db, current_user.id, request.task_ids, request.status, request.priority, request.category
    )
    return {"updated": count}


@router.post("/tasks/bulk-delete")
def bulk_delete_tasks(
    request: BulkDeleteTasksRequest,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Массовое удаление задач"""
    count = TaskService.bulk_delete_tasks(db, current_user.id, request.task_ids)
    return {"deleted": count}


# === AI Suggestions ===

@router.post("/ai-suggestions", response_model=TaskSuggestionsResponse)
def get_ai_suggestions(
    request: TaskSuggestionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Получить AI предложения задач
    
    AI анализирует контекст бизнеса и предлагает релевантные задачи.
    """
    return TaskService.generate_task_suggestions(request)


# === Statistics & Analytics ===

@router.get("/statistics", response_model=TaskStatistics)
def get_statistics(
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Получить статистику по задачам"""
    return TaskService.get_statistics(db, current_user.id)


@router.get("/productivity-report", response_model=ProductivityReport)
def get_productivity_report(
    period: str = Query("this_week", description="Период: today, this_week, this_month"),
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Получить отчёт по продуктивности"""
    if period not in ["today", "this_week", "this_month"]:
        raise HTTPException(status_code=400, detail="Invalid period")
    return TaskService.get_productivity_report(db, current_user.id, period)


# === Quick Actions ===

@router.post("/tasks/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Отметить задачу как выполненную"""
    task_update = TaskUpdate(status="done")
    task = TaskService.update_task(db, task_id, current_user.id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/tasks/{task_id}/start", response_model=Task)
def start_task(
    task_id: int,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Начать работу над задачей"""
    task_update = TaskUpdate(status="in_progress")
    task = TaskService.update_task(db, task_id, current_user.id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/tasks/{task_id}/cancel", response_model=Task)
def cancel_task(
    task_id: int,
    db: Session = Depends(get_db_sync),
    current_user: User = Depends(get_current_user)
):
    """Отменить задачу"""
    task_update = TaskUpdate(status="cancelled")
    task = TaskService.update_task(db, task_id, current_user.id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
