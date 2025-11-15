from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from app.models.task import Task
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskSuggestionRequest,
    TaskSuggestion,
    TaskSuggestionsResponse,
    TaskStatistics,
    ProductivityInsight,
    ProductivityReport,
)


class TaskService:
    """Сервис для работы с задачами"""

    # === CRUD Operations ===
    
    @staticmethod
    def create_task(db: Session, user_id: int, task: TaskCreate) -> Task:
        """Создать задачу"""
        db_task = Task(
            user_id=user_id,
            **task.model_dump()
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def get_tasks(
        db: Session,
        user_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        is_overdue: Optional[bool] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Получить список задач с фильтрами"""
        query = db.query(Task).filter(Task.user_id == user_id)
        
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if category:
            query = query.filter(Task.category == category)
        if is_overdue:
            now = datetime.utcnow()
            query = query.filter(
                and_(
                    Task.due_date < now,
                    Task.status != "done",
                    Task.status != "cancelled"
                )
            )
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern)
                )
            )
        
        return query.order_by(Task.due_date.asc().nullslast(), Task.priority.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_task(db: Session, task_id: int, user_id: int) -> Optional[Task]:
        """Получить задачу по ID"""
        return db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).first()

    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        user_id: int,
        task_update: TaskUpdate
    ) -> Optional[Task]:
        """Обновить задачу"""
        db_task = TaskService.get_task(db, task_id, user_id)
        if not db_task:
            return None
        
        update_data = task_update.model_dump(exclude_unset=True)
        
        # Автоматическая установка completed_at при смене статуса на done
        if update_data.get('status') == 'done' and db_task.status != 'done':
            update_data['completed_at'] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def delete_task(db: Session, task_id: int, user_id: int) -> bool:
        """Удалить задачу"""
        db_task = TaskService.get_task(db, task_id, user_id)
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True

    # === Bulk Operations ===

    @staticmethod
    def bulk_update_tasks(
        db: Session,
        user_id: int,
        task_ids: List[int],
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None
    ) -> int:
        """Массовое обновление задач"""
        query = db.query(Task).filter(
            Task.id.in_(task_ids),
            Task.user_id == user_id
        )
        
        update_data = {}
        if status:
            update_data['status'] = status
            if status == 'done':
                update_data['completed_at'] = datetime.utcnow()
        if priority:
            update_data['priority'] = priority
        if category:
            update_data['category'] = category
        
        if update_data:
            count = query.update(update_data, synchronize_session=False)
            db.commit()
            return count
        return 0

    @staticmethod
    def bulk_delete_tasks(db: Session, user_id: int, task_ids: List[int]) -> int:
        """Массовое удаление задач"""
        count = db.query(Task).filter(
            Task.id.in_(task_ids),
            Task.user_id == user_id
        ).delete(synchronize_session=False)
        db.commit()
        return count

    # === AI Suggestions ===

    @staticmethod
    def generate_task_suggestions(request: TaskSuggestionRequest) -> TaskSuggestionsResponse:
        """
        Генерация предложений задач с помощью AI
        TODO: Интеграция с Ollama/LiteLLM
        """
        # Шаблонные предложения (заменить на AI генерацию)
        templates = [
            {
                "title": "Проверить финансовые отчёты",
                "description": f"Проверить актуальность финансовых данных для: {request.context}",
                "priority": "high",
                "category": "finance",
                "estimated_minutes": 30,
                "tags": ["финансы", "отчёты"]
            },
            {
                "title": "Обновить маркетинговые материалы",
                "description": f"Создать новый контент для социальных сетей на тему: {request.context}",
                "priority": "medium",
                "category": "marketing",
                "estimated_minutes": 60,
                "tags": ["маркетинг", "соцсети"]
            },
            {
                "title": "Подготовить документы",
                "description": f"Создать необходимые документы для: {request.context}",
                "priority": "medium",
                "category": "documents",
                "estimated_minutes": 45,
                "tags": ["документы"]
            },
            {
                "title": "Проанализировать конкурентов",
                "description": f"Изучить конкурентов в сфере: {request.context}",
                "priority": "low",
                "category": "research",
                "estimated_minutes": 90,
                "tags": ["исследование", "конкуренты"]
            },
            {
                "title": "Встреча с клиентами",
                "description": f"Запланировать встречу для обсуждения: {request.context}",
                "priority": "high",
                "category": "meetings",
                "estimated_minutes": 60,
                "tags": ["встречи", "клиенты"]
            },
        ]
        
        suggestions = [
            TaskSuggestion(**template)
            for template in templates[:request.count]
        ]
        
        return TaskSuggestionsResponse(suggestions=suggestions)

    # === Statistics ===

    @staticmethod
    def get_statistics(db: Session, user_id: int) -> TaskStatistics:
        """Получить статистику по задачам"""
        tasks = db.query(Task).filter(Task.user_id == user_id).all()
        
        total = len(tasks)
        todo = sum(1 for t in tasks if t.status == "todo")
        in_progress = sum(1 for t in tasks if t.status == "in_progress")
        done = sum(1 for t in tasks if t.status == "done")
        cancelled = sum(1 for t in tasks if t.status == "cancelled")
        
        # Просроченные задачи
        now = datetime.utcnow()
        overdue = sum(1 for t in tasks if t.due_date and t.due_date < now and t.status not in ["done", "cancelled"])
        
        # Задачи на сегодня
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        today = sum(1 for t in tasks if t.due_date and today_start <= t.due_date < today_end)
        
        # Задачи на этой неделе
        week_start = today_start - timedelta(days=today_start.weekday())
        week_end = week_start + timedelta(days=7)
        this_week = sum(1 for t in tasks if t.due_date and week_start <= t.due_date < week_end)
        
        # Приоритеты
        high_priority = sum(1 for t in tasks if t.priority == "high")
        urgent_priority = sum(1 for t in tasks if t.priority == "urgent")
        
        # Процент выполнения
        completion_rate = 0.0
        if total > 0:
            completion_rate = (done / total) * 100
        
        # Среднее время выполнения
        completed_tasks_with_time = [t for t in tasks if t.status == "done" and t.actual_minutes]
        avg_completion = None
        if completed_tasks_with_time:
            avg_completion = sum(t.actual_minutes for t in completed_tasks_with_time) / len(completed_tasks_with_time)
        
        # Группировка по категориям
        categories: Dict[str, int] = {}
        for task in tasks:
            if task.category:
                categories[task.category] = categories.get(task.category, 0) + 1
        
        # Группировка по приоритетам
        priorities: Dict[str, int] = {}
        for task in tasks:
            priorities[task.priority] = priorities.get(task.priority, 0) + 1
        
        return TaskStatistics(
            total_tasks=total,
            todo_tasks=todo,
            in_progress_tasks=in_progress,
            done_tasks=done,
            cancelled_tasks=cancelled,
            overdue_tasks=overdue,
            today_tasks=today,
            this_week_tasks=this_week,
            high_priority_tasks=high_priority,
            urgent_priority_tasks=urgent_priority,
            completion_rate=round(completion_rate, 2),
            average_completion_minutes=round(avg_completion, 2) if avg_completion else None,
            tasks_by_category=categories,
            tasks_by_priority=priorities
        )

    # === Productivity Insights ===

    @staticmethod
    def get_productivity_report(db: Session, user_id: int, period: str = "this_week") -> ProductivityReport:
        """Получить отчёт по продуктивности"""
        now = datetime.utcnow()
        
        # Определить период
        if period == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "this_week":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=now.weekday())
        else:  # this_month
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Получить выполненные задачи за период
        completed_tasks = db.query(Task).filter(
            Task.user_id == user_id,
            Task.status == "done",
            Task.completed_at >= start
        ).all()
        
        total_time = sum(t.actual_minutes for t in completed_tasks if t.actual_minutes) or 0
        
        # Самая продуктивная категория
        categories: Dict[str, int] = {}
        for task in completed_tasks:
            if task.category:
                categories[task.category] = categories.get(task.category, 0) + 1
        
        most_productive = max(categories.items(), key=lambda x: x[1])[0] if categories else None
        
        # Генерация инсайтов
        insights = TaskService._generate_insights(completed_tasks, period)
        
        return ProductivityReport(
            period=period,
            completed_tasks=len(completed_tasks),
            total_time_minutes=total_time,
            most_productive_category=most_productive,
            insights=insights
        )

    @staticmethod
    def _generate_insights(tasks: List[Task], period: str) -> List[ProductivityInsight]:
        """Генерация инсайтов по продуктивности"""
        insights = []
        
        completed_count = len(tasks)
        
        if completed_count == 0:
            insights.append(ProductivityInsight(
                type="warning",
                title="Нет выполненных задач",
                message=f"За период '{period}' не выполнено ни одной задачи.",
                action="Начните с простых задач!"
            ))
        elif completed_count >= 10:
            insights.append(ProductivityInsight(
                type="achievement",
                title="Отличная продуктивность!",
                message=f"Выполнено {completed_count} задач за период '{period}'!",
                action=None
            ))
        
        # Проверка на задачи с оценкой времени
        tasks_with_estimate = [t for t in tasks if t.estimated_minutes and t.actual_minutes]
        if tasks_with_estimate:
            avg_diff = sum(abs(t.actual_minutes - t.estimated_minutes) for t in tasks_with_estimate) / len(tasks_with_estimate)
            if avg_diff > 30:
                insights.append(ProductivityInsight(
                    type="tip",
                    title="Улучшите оценку времени",
                    message=f"В среднем отклонение от оценки: {int(avg_diff)} минут.",
                    action="Попробуйте более точно оценивать задачи"
                ))
        
        return insights

    # === Recurring Tasks ===

    @staticmethod
    def create_recurring_instances(db: Session, task: Task, count: int = 4) -> List[Task]:
        """Создать экземпляры повторяющейся задачи"""
        if not task.is_recurring or not task.recurrence_pattern:
            return []
        
        instances = []
        base_due_date = task.due_date or datetime.utcnow()
        
        for i in range(1, count + 1):
            # Вычислить новую дату
            if task.recurrence_pattern == "daily":
                new_due_date = base_due_date + timedelta(days=i)
            elif task.recurrence_pattern == "weekly":
                new_due_date = base_due_date + timedelta(weeks=i)
            elif task.recurrence_pattern == "monthly":
                new_due_date = base_due_date + timedelta(days=30 * i)
            else:
                continue
            
            # Создать новый экземпляр
            new_task = Task(
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                priority=task.priority,
                status="todo",
                due_date=new_due_date,
                category=task.category,
                tags=task.tags,
                estimated_minutes=task.estimated_minutes,
                is_recurring=True,
                recurrence_pattern=task.recurrence_pattern,
                parent_task_id=task.id
            )
            db.add(new_task)
            instances.append(new_task)
        
        db.commit()
        return instances
