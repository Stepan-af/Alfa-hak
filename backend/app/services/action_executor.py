"""
Action Executor Service - Cross-module operations.
Execute actions suggested by AI across different modules.
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.task import Task
from app.models.finance import FinanceRecord
from app.models.document import Document
from app.models.marketing import MarketingCampaign
from app.schemas.task import TaskCreate
from app.schemas.finance import FinanceRecordCreate
from app.schemas.document import DocumentCreate
from app.schemas.marketing import MarketingCampaignCreate


class ActionExecutor:
    """Execute cross-module actions based on AI suggestions."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============= Task Actions =============
    
    def create_task_from_suggestion(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[datetime] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        ai_context: Optional[str] = None
    ) -> Task:
        """Create a task from AI suggestion."""
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            status="todo",
            due_date=due_date,
            category=category,
            tags=tags,
            ai_suggested=True,
            ai_context=ai_context
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def create_tasks_bulk(
        self,
        user_id: int,
        tasks_data: List[Dict[str, Any]]
    ) -> List[Task]:
        """Create multiple tasks at once."""
        tasks = []
        for data in tasks_data:
            task = Task(
                user_id=user_id,
                title=data["title"],
                description=data.get("description"),
                priority=data.get("priority", "medium"),
                status="todo",
                due_date=data.get("due_date"),
                category=data.get("category"),
                tags=data.get("tags"),
                ai_suggested=True,
                ai_context=data.get("ai_context")
            )
            tasks.append(task)
        
        self.db.add_all(tasks)
        self.db.commit()
        for task in tasks:
            self.db.refresh(task)
        return tasks
    
    # ============= Finance Actions =============
    
    def analyze_finance_period(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze finance records for a period."""
        records = self.db.query(FinanceRecord).filter(
            FinanceRecord.user_id == user_id,
            FinanceRecord.date >= start_date,
            FinanceRecord.date <= end_date
        ).all()
        
        income = sum(float(r.amount) for r in records if r.type == "income")
        expense = sum(float(r.amount) for r in records if r.type == "expense")
        balance = income - expense
        
        # Category breakdown
        categories: Dict[str, float] = {}
        for record in records:
            cat = record.category or "Без категории"
            categories[cat] = categories.get(cat, 0) + float(record.amount)
        
        return {
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "total_income": round(income, 2),
            "total_expense": round(expense, 2),
            "balance": round(balance, 2),
            "records_count": len(records),
            "categories": categories,
            "top_expense_category": max(
                [(cat, amt) for cat, amt in categories.items() if amt < 0],
                key=lambda x: abs(x[1]),
                default=(None, 0)
            )[0] if categories else None
        }
    
    def create_finance_record_from_text(
        self,
        user_id: int,
        amount: float,
        description: str,
        record_type: str,
        category: Optional[str] = None,
        date: Optional[datetime] = None
    ) -> FinanceRecord:
        """Create finance record from natural language."""
        record = FinanceRecord(
            user_id=user_id,
            amount=abs(amount),
            type=record_type,
            description=description,
            category=category or "Прочее",
            date=date or datetime.utcnow()
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record
    
    # ============= Document Actions =============
    
    def generate_document_from_template(
        self,
        user_id: int,
        template_type: str,
        variables: Dict[str, Any]
    ) -> Document:
        """Generate document from template with variables."""
        # Simple template rendering
        templates = {
            "contract": """
ДОГОВОР №{contract_number}

Заказчик: {client_name}
ИНН: {client_inn}

Исполнитель: {company_name}
ИНН: {company_inn}

Предмет договора: {subject}
Стоимость: {amount} руб.

Дата: {date}
            """,
            "invoice": """
СЧЕТ НА ОПЛАТУ №{invoice_number}

От: {date}
Поставщик: {company_name}
Покупатель: {client_name}

Наименование: {description}
Сумма: {amount} руб.
НДС: {vat} руб.
Итого: {total} руб.
            """,
            "act": """
АКТ ВЫПОЛНЕННЫХ РАБОТ №{act_number}

От: {date}
Заказчик: {client_name}
Исполнитель: {company_name}

Описание работ: {description}
Стоимость: {amount} руб.

Работы выполнены в полном объеме.
            """
        }
        
        template_content = templates.get(template_type, "Шаблон не найден")
        content = template_content.format(**variables)
        
        document = Document(
            user_id=user_id,
            title=f"{template_type.upper()} от {datetime.now().strftime('%d.%m.%Y')}",
            content=content,
            doc_type=template_type,
            metadata_=variables
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    # ============= Marketing Actions =============
    
    def create_marketing_campaign_from_idea(
        self,
        user_id: int,
        name: str,
        platform: str,
        content_type: str,
        target_audience: Optional[str] = None,
        budget: Optional[float] = None,
        ai_prompt: Optional[str] = None
    ) -> MarketingCampaign:
        """Create marketing campaign from AI-generated idea."""
        campaign = MarketingCampaign(
            user_id=user_id,
            name=name,
            platform=platform,
            status="draft",
            budget=budget,
            content_type=content_type,
            target_audience=target_audience,
            ai_generated=True,
            ai_prompt=ai_prompt
        )
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign
    
    def schedule_campaign_tasks(
        self,
        user_id: int,
        campaign_id: int,
        campaign_name: str
    ) -> List[Task]:
        """Create tasks for marketing campaign execution."""
        campaign_tasks = [
            {
                "title": f"Подготовить контент для {campaign_name}",
                "description": f"Создать визуалы и тексты для кампании #{campaign_id}",
                "category": "marketing",
                "priority": "high",
                "due_date": datetime.utcnow() + timedelta(days=3)
            },
            {
                "title": f"Настроить таргетинг для {campaign_name}",
                "description": f"Настроить рекламные кабинеты для кампании #{campaign_id}",
                "category": "marketing",
                "priority": "high",
                "due_date": datetime.utcnow() + timedelta(days=5)
            },
            {
                "title": f"Запустить кампанию {campaign_name}",
                "description": f"Активировать рекламную кампанию #{campaign_id}",
                "category": "marketing",
                "priority": "urgent",
                "due_date": datetime.utcnow() + timedelta(days=7)
            },
            {
                "title": f"Проанализировать результаты {campaign_name}",
                "description": f"Собрать метрики и проанализировать эффективность кампании #{campaign_id}",
                "category": "marketing",
                "priority": "medium",
                "due_date": datetime.utcnow() + timedelta(days=14)
            }
        ]
        
        return self.create_tasks_bulk(user_id, campaign_tasks)
    
    # ============= Unified Actions =============
    
    def execute_action(
        self,
        user_id: int,
        action_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute any action based on type and parameters.
        Universal action dispatcher.
        """
        action_map = {
            "create_task": self._exec_create_task,
            "create_tasks_bulk": self._exec_create_tasks_bulk,
            "analyze_finance": self._exec_analyze_finance,
            "add_expense": self._exec_add_expense,
            "add_income": self._exec_add_income,
            "generate_document": self._exec_generate_document,
            "create_campaign": self._exec_create_campaign,
            "schedule_campaign": self._exec_schedule_campaign,
        }
        
        executor = action_map.get(action_type)
        if not executor:
            return {
                "success": False,
                "message": f"Unknown action type: {action_type}",
                "data": None
            }
        
        try:
            result = executor(user_id, parameters)
            return {
                "success": True,
                "message": f"Action '{action_type}' executed successfully",
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error executing action: {str(e)}",
                "data": None
            }
    
    # Private executors
    def _exec_create_task(self, user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        task = self.create_task_from_suggestion(
            user_id=user_id,
            title=params["title"],
            description=params.get("description"),
            priority=params.get("priority", "medium"),
            category=params.get("category"),
            tags=params.get("tags"),
            ai_context=params.get("ai_context")
        )
        return {"id": task.id, "title": task.title}
    
    def _exec_create_tasks_bulk(self, user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        tasks = self.create_tasks_bulk(user_id, params["tasks"])
        return {"count": len(tasks), "tasks": [{"id": t.id, "title": t.title} for t in tasks]}
    
    def _exec_analyze_finance(self, user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        start_date = datetime.fromisoformat(params["start_date"])
        end_date = datetime.fromisoformat(params["end_date"])
        return self.analyze_finance_period(user_id, start_date, end_date)
    
    def _exec_add_expense(self, user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        record = self.create_finance_record_from_text(
            user_id=user_id,
            amount=params["amount"],
            description=params["description"],
            record_type="expense",
            category=params.get("category")
        )
        return {"id": record.id, "amount": float(record.amount)}
    
    def _exec_add_income(self, user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        record = self.create_finance_record_from_text(
            user_id=user_id,
            amount=params["amount"],
            description=params["description"],
            record_type="income",
            category=params.get("category")
        )
        return {"id": record.id, "amount": float(record.amount)}
    
    def _exec_generate_document(self, user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        document = self.generate_document_from_template(
            user_id=user_id,
            template_type=params["template_type"],
            variables=params["variables"]
        )
        return {"id": document.id, "title": document.title}
    
    def _exec_create_campaign(self, user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        campaign = self.create_marketing_campaign_from_idea(
            user_id=user_id,
            name=params["name"],
            platform=params["platform"],
            content_type=params["content_type"],
            target_audience=params.get("target_audience"),
            budget=params.get("budget")
        )
        return {"id": campaign.id, "name": campaign.name}
    
    def _exec_schedule_campaign(self, user_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        tasks = self.schedule_campaign_tasks(
            user_id=user_id,
            campaign_id=params["campaign_id"],
            campaign_name=params["campaign_name"]
        )
        return {"tasks_created": len(tasks), "campaign_id": params["campaign_id"]}
