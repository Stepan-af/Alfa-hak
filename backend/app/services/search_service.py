"""
Unified Search Service - Search across all modules.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime

from app.models.task import Task
from app.models.finance import FinanceRecord
from app.models.document import Document
from app.models.marketing import MarketingCampaign


class UnifiedSearchService:
    """Search across tasks, finance, documents, and marketing."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def search_all(
        self,
        user_id: int,
        query: str,
        limit: int = 50
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across all modules.
        Returns results grouped by module.
        """
        query_lower = query.lower()
        
        results = {
            "tasks": self._search_tasks(user_id, query_lower, limit),
            "finance": self._search_finance(user_id, query_lower, limit),
            "documents": self._search_documents(user_id, query_lower, limit),
            "marketing": self._search_marketing(user_id, query_lower, limit)
        }
        
        # Calculate total count
        total = sum(len(items) for items in results.values())
        results["_meta"] = {
            "query": query,
            "total_results": total,
            "search_time": datetime.utcnow().isoformat()
        }
        
        return results
    
    def _search_tasks(
        self,
        user_id: int,
        query: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search in tasks."""
        tasks = self.db.query(Task).filter(
            Task.user_id == user_id,
            or_(
                Task.title.ilike(f"%{query}%"),
                Task.description.ilike(f"%{query}%"),
                Task.category.ilike(f"%{query}%")
            )
        ).limit(limit).all()
        
        return [
            {
                "id": task.id,
                "type": "task",
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "category": task.category,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "relevance_score": self._calculate_relevance(query, task.title, task.description)
            }
            for task in tasks
        ]
    
    def _search_finance(
        self,
        user_id: int,
        query: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search in finance records."""
        records = self.db.query(FinanceRecord).filter(
            FinanceRecord.user_id == user_id,
            or_(
                FinanceRecord.description.ilike(f"%{query}%"),
                FinanceRecord.category.ilike(f"%{query}%")
            )
        ).order_by(FinanceRecord.date.desc()).limit(limit).all()
        
        return [
            {
                "id": record.id,
                "type": "finance",
                "title": f"{record.type}: {record.description}",
                "description": f"{float(record.amount)} руб. - {record.category}",
                "amount": float(record.amount),
                "record_type": record.type,
                "category": record.category,
                "date": record.date.isoformat(),
                "created_at": record.created_at.isoformat() if record.created_at else None,
                "relevance_score": self._calculate_relevance(query, record.description, record.category)
            }
            for record in records
        ]
    
    def _search_documents(
        self,
        user_id: int,
        query: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search in documents."""
        documents = self.db.query(Document).filter(
            Document.user_id == user_id,
            or_(
                Document.title.ilike(f"%{query}%"),
                Document.content.ilike(f"%{query}%"),
                Document.doc_type.ilike(f"%{query}%")
            )
        ).order_by(Document.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": doc.id,
                "type": "document",
                "title": doc.title,
                "description": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                "doc_type": doc.doc_type,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "relevance_score": self._calculate_relevance(query, doc.title, doc.content)
            }
            for doc in documents
        ]
    
    def _search_marketing(
        self,
        user_id: int,
        query: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search in marketing campaigns."""
        campaigns = self.db.query(MarketingCampaign).filter(
            MarketingCampaign.user_id == user_id,
            or_(
                MarketingCampaign.name.ilike(f"%{query}%"),
                MarketingCampaign.description.ilike(f"%{query}%"),
                MarketingCampaign.platform.ilike(f"%{query}%")
            )
        ).order_by(MarketingCampaign.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": campaign.id,
                "type": "marketing",
                "title": campaign.name,
                "description": campaign.description or f"Кампания на {campaign.platform}",
                "platform": campaign.platform,
                "status": campaign.status,
                "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
                "relevance_score": self._calculate_relevance(query, campaign.name, campaign.description)
            }
            for campaign in campaigns
        ]
    
    def _calculate_relevance(
        self,
        query: str,
        title: Optional[str],
        content: Optional[str]
    ) -> float:
        """
        Calculate relevance score (0.0 to 1.0).
        Simple keyword matching for now.
        """
        score = 0.0
        query_words = set(query.lower().split())
        
        if title:
            title_words = set(title.lower().split())
            title_overlap = len(query_words & title_words)
            score += title_overlap * 0.3  # Title matches weighted higher
        
        if content:
            content_words = set(content.lower().split())
            content_overlap = len(query_words & content_words)
            score += content_overlap * 0.1
        
        # Check for exact phrase match
        if title and query in title.lower():
            score += 0.5
        if content and query in content.lower():
            score += 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    def search_by_type(
        self,
        user_id: int,
        query: str,
        search_type: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search in specific module only."""
        query_lower = query.lower()
        
        if search_type == "tasks":
            return self._search_tasks(user_id, query_lower, limit)
        elif search_type == "finance":
            return self._search_finance(user_id, query_lower, limit)
        elif search_type == "documents":
            return self._search_documents(user_id, query_lower, limit)
        elif search_type == "marketing":
            return self._search_marketing(user_id, query_lower, limit)
        else:
            return []
    
    def get_recent_activity(
        self,
        user_id: int,
        days: int = 7,
        limit: int = 20
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get recent activity across all modules."""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Recent tasks
        recent_tasks = self.db.query(Task).filter(
            Task.user_id == user_id,
            Task.created_at >= cutoff_date
        ).order_by(Task.created_at.desc()).limit(limit).all()
        
        # Recent finance
        recent_finance = self.db.query(FinanceRecord).filter(
            FinanceRecord.user_id == user_id,
            FinanceRecord.date >= cutoff_date
        ).order_by(FinanceRecord.date.desc()).limit(limit).all()
        
        # Recent documents
        recent_docs = self.db.query(Document).filter(
            Document.user_id == user_id,
            Document.created_at >= cutoff_date
        ).order_by(Document.created_at.desc()).limit(limit).all()
        
        # Recent marketing
        recent_marketing = self.db.query(MarketingCampaign).filter(
            MarketingCampaign.user_id == user_id,
            MarketingCampaign.created_at >= cutoff_date
        ).order_by(MarketingCampaign.created_at.desc()).limit(limit).all()
        
        return {
            "tasks": [
                {
                    "id": t.id,
                    "type": "task",
                    "title": t.title,
                    "status": t.status,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                }
                for t in recent_tasks
            ],
            "finance": [
                {
                    "id": r.id,
                    "type": "finance",
                    "title": r.description,
                    "amount": float(r.amount),
                    "record_type": r.type,
                    "date": r.date.isoformat()
                }
                for r in recent_finance
            ],
            "documents": [
                {
                    "id": d.id,
                    "type": "document",
                    "title": d.title,
                    "doc_type": d.doc_type,
                    "created_at": d.created_at.isoformat() if d.created_at else None
                }
                for d in recent_docs
            ],
            "marketing": [
                {
                    "id": c.id,
                    "type": "marketing",
                    "title": c.name,
                    "platform": c.platform,
                    "status": c.status,
                    "created_at": c.created_at.isoformat() if c.created_at else None
                }
                for c in recent_marketing
            ]
        }
