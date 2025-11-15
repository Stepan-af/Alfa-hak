"""
Chat service with LLM integration and RAG (Retrieval-Augmented Generation).
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
import httpx
import json

from app.models.chat import ChatConversation, ChatMessage
from app.models.user import User
from app.models.task import Task
from app.models.finance import FinanceRecord
from app.models.marketing import MarketingCampaign
from app.models.document import Document
from app.schemas.chat import (
    ChatMessageCreate, ChatConversationCreate, ChatConversationUpdate,
    RAGContext, ContextDocument, ContextTask, ContextFinance, ContextMarketing,
    SuggestedAction, ChatStatistics
)


class ChatService:
    """Service for chat operations with LLM integration."""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_base_url = "http://litellm:4000"  # LiteLLM proxy
        self.model_name = "llama3.2"  # Lighter model for Docker environment
        self.llm_api_key = "sk-1234"  # LiteLLM master key
        
    # ============= Conversation Management =============
    
    def create_conversation(
        self,
        user_id: int,
        data: ChatConversationCreate
    ) -> ChatConversation:
        """Create a new conversation."""
        conversation = ChatConversation(
            user_id=user_id,
            title=data.title or "Новый разговор",
            metadata_=data.metadata
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def get_conversations(
        self,
        user_id: int,
        include_archived: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> List[ChatConversation]:
        """Get user's conversations."""
        query = self.db.query(ChatConversation).filter(
            ChatConversation.user_id == user_id
        )
        
        if not include_archived:
            query = query.filter(ChatConversation.is_archived == False)
        
        return query.order_by(desc(ChatConversation.updated_at)).offset(skip).limit(limit).all()
    
    def get_conversation(self, conversation_id: int, user_id: int) -> Optional[ChatConversation]:
        """Get conversation by ID."""
        return self.db.query(ChatConversation).filter(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == user_id
        ).first()
    
    def update_conversation(
        self,
        conversation_id: int,
        user_id: int,
        data: ChatConversationUpdate
    ) -> Optional[ChatConversation]:
        """Update conversation."""
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return None
        
        if data.title is not None:
            conversation.title = data.title
        if data.is_archived is not None:
            conversation.is_archived = data.is_archived
        if data.metadata is not None:
            conversation.metadata_ = data.metadata
        
        conversation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """Delete conversation."""
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return False
        
        self.db.delete(conversation)
        self.db.commit()
        return True
    
    # ============= Message Management =============
    
    async def send_message(
        self,
        user_id: int,
        data: ChatMessageCreate
    ) -> ChatMessage:
        """Send message and get AI response."""
        # Get or create conversation
        if data.conversation_id:
            conversation = self.get_conversation(data.conversation_id, user_id)
            if not conversation:
                raise ValueError("Conversation not found")
        else:
            conversation = self.create_conversation(
                user_id,
                ChatConversationCreate(title=self._generate_title(data.content))
            )
        
        # Create user message
        user_message = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=data.content
        )
        self.db.add(user_message)
        self.db.commit()
        self.db.refresh(user_message)
        
        # Retrieve context (RAG)
        context = await self._retrieve_context(user_id, data.content)
        
        # Generate AI response
        ai_response = await self._generate_response(
            conversation_id=conversation.id,
            user_message=data.content,
            context=context
        )
        
        # Create assistant message
        assistant_message = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response["content"],
            tokens_used=ai_response.get("tokens_used"),
            model_used=ai_response.get("model_used"),
            context_documents=context.get("document_ids"),
            context_tasks=context.get("task_ids"),
            context_finance=context.get("finance_ids"),
            context_marketing=context.get("marketing_ids")
        )
        self.db.add(assistant_message)
        
        # Update conversation timestamp and title
        conversation.updated_at = datetime.utcnow()
        if conversation.title == "Новый разговор":
            conversation.title = self._generate_title(data.content)
        
        self.db.commit()
        self.db.refresh(assistant_message)
        
        return assistant_message
    
    def get_messages(
        self,
        conversation_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatMessage]:
        """Get conversation messages."""
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return []
        
        return self.db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at).offset(skip).limit(limit).all()
    
    def rate_message(
        self,
        message_id: int,
        user_id: int,
        rating: int,
        feedback: Optional[str] = None
    ) -> Optional[ChatMessage]:
        """Rate an assistant message."""
        message = self.db.query(ChatMessage).join(ChatConversation).filter(
            ChatMessage.id == message_id,
            ChatConversation.user_id == user_id,
            ChatMessage.role == "assistant"
        ).first()
        
        if not message:
            return None
        
        message.user_rating = rating
        message.user_feedback = feedback
        self.db.commit()
        self.db.refresh(message)
        return message
    
    # ============= RAG (Retrieval-Augmented Generation) =============
    
    async def _retrieve_context(self, user_id: int, query: str) -> Dict[str, Any]:
        """Retrieve relevant context from user's data."""
        context = {
            "documents": [],
            "tasks": [],
            "finance": [],
            "marketing": [],
            "document_ids": [],
            "task_ids": [],
            "finance_ids": [],
            "marketing_ids": []
        }
        
        # Retrieve recent tasks (last 20)
        tasks = self.db.query(Task).filter(
            Task.user_id == user_id
        ).order_by(desc(Task.created_at)).limit(20).all()
        
        for task in tasks:
            if self._is_relevant(query, task.title, task.description):
                context["tasks"].append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None
                })
                context["task_ids"].append(task.id)
        
        # Retrieve recent finance records (last 30)
        finance_records = self.db.query(FinanceRecord).filter(
            FinanceRecord.user_id == user_id
        ).order_by(desc(FinanceRecord.date)).limit(30).all()
        
        for record in finance_records:
            if self._is_relevant(query, record.description, record.category):
                context["finance"].append({
                    "id": record.id,
                    "description": record.description,
                    "amount": float(record.amount),
                    "type": record.type,
                    "category": record.category,
                    "date": record.date.isoformat()
                })
                context["finance_ids"].append(record.id)
        
        # Retrieve documents (last 10)
        documents = self.db.query(Document).filter(
            Document.user_id == user_id
        ).order_by(desc(Document.created_at)).limit(10).all()
        
        for doc in documents:
            if self._is_relevant(query, doc.title, doc.content):
                context["documents"].append({
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content[:500]  # First 500 chars
                })
                context["document_ids"].append(doc.id)
        
        # Retrieve marketing campaigns (last 10)
        campaigns = self.db.query(MarketingCampaign).filter(
            MarketingCampaign.user_id == user_id
        ).order_by(desc(MarketingCampaign.created_at)).limit(10).all()
        
        for campaign in campaigns:
            if self._is_relevant(query, campaign.title, campaign.description):
                context["marketing"].append({
                    "id": campaign.id,
                    "name": campaign.title,
                    "platform": campaign.platform,
                    "status": campaign.status
                })
                context["marketing_ids"].append(campaign.id)
        
        return context
    
    def _is_relevant(self, query: str, *texts: Optional[str]) -> bool:
        """Simple relevance check (can be improved with embeddings)."""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for text in texts:
            if not text:
                continue
            text_lower = text.lower()
            text_words = set(text_lower.split())
            
            # Check for keyword overlap
            overlap = query_words & text_words
            if len(overlap) >= 2:  # At least 2 common words
                return True
            
            # Check for substring match
            if any(word in text_lower for word in query_words if len(word) > 3):
                return True
        
        return False
    
    # ============= LLM Integration =============
    
    async def _generate_response(
        self,
        conversation_id: int,
        user_message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI response using LLM."""
        # Get conversation history
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at).limit(10).all()
        
        # Build system prompt with context
        system_prompt = self._build_system_prompt(context)
        
        # Build message history for LLM
        llm_messages = [{"role": "system", "content": system_prompt}]
        
        for msg in messages[-5:]:  # Last 5 messages for context
            llm_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        llm_messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Call LLM API
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.llm_base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.llm_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model_name,
                        "messages": llm_messages,
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "tokens_used": data.get("usage", {}).get("total_tokens"),
                    "model_used": self.model_name
                }
        except Exception as e:
            # Fallback response if LLM fails
            return {
                "content": f"Извините, я временно недоступен. Попробуйте позже. (Ошибка: {str(e)[:100]})",
                "tokens_used": None,
                "model_used": None
            }
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt with RAG context."""
        prompt = """Ты - AI-помощник для малого бизнеса "Альфа Копилот". 
Ты помогаешь предпринимателям с финансами, задачами, документами и маркетингом.
Отвечай кратко, по делу и дружелюбно. Используй эмодзи где уместно.

ВАЖНО: Если пользователь просит выполнить действие (создать задачу, добавить расход, сгенерировать документ),
в конце своего ответа добавь специальный маркер:
[ACTION:тип_действия:параметры]

Доступные действия:
- [ACTION:create_task:Название задачи|Описание|Приоритет|Категория]
- [ACTION:add_expense:Сумма|Описание|Категория]
- [ACTION:add_income:Сумма|Описание|Категория]
- [ACTION:analyze_finance:Дата_начала|Дата_конца]
- [ACTION:generate_document:Тип|Параметры]
- [ACTION:create_campaign:Название|Платформа|Тип_контента]

"""
        
        # Add context sections
        if context.get("tasks"):
            prompt += "\n📋 ТЕКУЩИЕ ЗАДАЧИ:\n"
            for task in context["tasks"][:5]:
                prompt += f"- [{task['status']}] {task['title']} (приоритет: {task['priority']})\n"
        
        if context.get("finance"):
            prompt += "\n💰 ПОСЛЕДНИЕ ФИНАНСОВЫЕ ОПЕРАЦИИ:\n"
            for record in context["finance"][:5]:
                prompt += f"- {record['type']}: {record['amount']} руб. - {record['description']}\n"
        
        if context.get("marketing"):
            prompt += "\n📢 МАРКЕТИНГОВЫЕ КАМПАНИИ:\n"
            for campaign in context["marketing"][:3]:
                prompt += f"- {campaign['name']} на {campaign['platform']} ({campaign['status']})\n"
        
        if context.get("documents"):
            prompt += "\n📄 ДОКУМЕНТЫ:\n"
            for doc in context["documents"][:3]:
                prompt += f"- {doc['title']}\n"
        
        prompt += "\nИспользуй эту информацию для персонализированных ответов."
        
        return prompt
    
    def _generate_title(self, first_message: str) -> str:
        """Generate conversation title from first message."""
        title = first_message[:50].strip()
        if len(first_message) > 50:
            title += "..."
        return title
    
    # ============= Analytics =============
    
    def get_statistics(self, user_id: int) -> ChatStatistics:
        """Get chat statistics for user."""
        total_conversations = self.db.query(func.count(ChatConversation.id)).filter(
            ChatConversation.user_id == user_id
        ).scalar() or 0
        
        total_messages = self.db.query(func.count(ChatMessage.id)).join(ChatConversation).filter(
            ChatConversation.user_id == user_id
        ).scalar() or 0
        
        avg_messages = total_messages / total_conversations if total_conversations > 0 else 0
        
        total_tokens = self.db.query(func.sum(ChatMessage.tokens_used)).join(ChatConversation).filter(
            ChatConversation.user_id == user_id,
            ChatMessage.tokens_used.isnot(None)
        ).scalar() or 0
        
        # Most used model
        most_used_model = self.db.query(
            ChatMessage.model_used,
            func.count(ChatMessage.id).label("count")
        ).join(ChatConversation).filter(
            ChatConversation.user_id == user_id,
            ChatMessage.model_used.isnot(None)
        ).group_by(ChatMessage.model_used).order_by(desc("count")).first()
        
        # Average rating
        avg_rating = self.db.query(func.avg(ChatMessage.user_rating)).join(ChatConversation).filter(
            ChatConversation.user_id == user_id,
            ChatMessage.user_rating.isnot(None)
        ).scalar()
        
        return ChatStatistics(
            total_conversations=total_conversations,
            total_messages=total_messages,
            avg_messages_per_conversation=round(avg_messages, 2),
            total_tokens_used=int(total_tokens),
            most_used_model=most_used_model[0] if most_used_model else None,
            avg_user_rating=round(float(avg_rating), 2) if avg_rating else None
        )
    
    # ============= Intent Parsing & Actions =============
    
    def parse_suggested_actions(self, ai_response: str) -> List[Dict[str, Any]]:
        """
        Parse action markers from AI response.
        Format: [ACTION:type:param1|param2|param3]
        """
        import re
        actions = []
        
        # Find all action markers
        pattern = r'\[ACTION:([^:]+):([^\]]+)\]'
        matches = re.findall(pattern, ai_response)
        
        for action_type, params_str in matches:
            params = params_str.split('|')
            
            # Map action types to structured data
            if action_type == 'create_task' and len(params) >= 1:
                actions.append({
                    "type": "create_task",
                    "title": "Создать задачу",
                    "description": f"Создать: {params[0]}",
                    "parameters": {
                        "title": params[0],
                        "description": params[1] if len(params) > 1 else None,
                        "priority": params[2] if len(params) > 2 else "medium",
                        "category": params[3] if len(params) > 3 else None
                    },
                    "confidence": 0.9
                })
            
            elif action_type == 'add_expense' and len(params) >= 2:
                actions.append({
                    "type": "add_expense",
                    "title": "Добавить расход",
                    "description": f"Расход: {params[1]} на сумму {params[0]} руб.",
                    "parameters": {
                        "amount": float(params[0]),
                        "description": params[1],
                        "category": params[2] if len(params) > 2 else "Прочее"
                    },
                    "confidence": 0.95
                })
            
            elif action_type == 'add_income' and len(params) >= 2:
                actions.append({
                    "type": "add_income",
                    "title": "Добавить доход",
                    "description": f"Доход: {params[1]} на сумму {params[0]} руб.",
                    "parameters": {
                        "amount": float(params[0]),
                        "description": params[1],
                        "category": params[2] if len(params) > 2 else "Прочее"
                    },
                    "confidence": 0.95
                })
            
            elif action_type == 'analyze_finance' and len(params) >= 2:
                actions.append({
                    "type": "analyze_finance",
                    "title": "Анализ финансов",
                    "description": f"Проанализировать финансы за период",
                    "parameters": {
                        "start_date": params[0],
                        "end_date": params[1]
                    },
                    "confidence": 0.85
                })
            
            elif action_type == 'generate_document' and len(params) >= 1:
                actions.append({
                    "type": "generate_document",
                    "title": "Создать документ",
                    "description": f"Сгенерировать {params[0]}",
                    "parameters": {
                        "template_type": params[0],
                        "variables": {}  # Will be filled from params[1] if provided
                    },
                    "confidence": 0.8
                })
            
            elif action_type == 'create_campaign' and len(params) >= 3:
                actions.append({
                    "type": "create_campaign",
                    "title": "Создать кампанию",
                    "description": f"Запустить {params[0]} на {params[1]}",
                    "parameters": {
                        "name": params[0],
                        "platform": params[1],
                        "content_type": params[2]
                    },
                    "confidence": 0.85
                })
        
        return actions
    
    def detect_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Detect user intent from message using keyword matching.
        Returns intent type and confidence.
        """
        message_lower = user_message.lower()
        
        # Task-related intents
        task_keywords = ['задач', 'дело', 'напомни', 'todo', 'сделать', 'выполнить']
        if any(kw in message_lower for kw in task_keywords):
            if any(word in message_lower for word in ['создай', 'добавь', 'новая', 'новое']):
                return {"intent": "create_task", "confidence": 0.8}
            if any(word in message_lower for word in ['покажи', 'список', 'какие']):
                return {"intent": "list_tasks", "confidence": 0.9}
            if any(word in message_lower for word in ['просроч', 'overdue']):
                return {"intent": "show_overdue_tasks", "confidence": 0.95}
        
        # Finance-related intents
        finance_keywords = ['финанс', 'деньги', 'расход', 'доход', 'бюджет', 'прибыль', 'баланс']
        if any(kw in message_lower for kw in finance_keywords):
            if any(word in message_lower for word in ['анализ', 'покажи', 'сколько']):
                return {"intent": "analyze_finance", "confidence": 0.85}
            if any(word in message_lower for word in ['добавь', 'записать', 'потратил']):
                return {"intent": "add_expense", "confidence": 0.9}
            if any(word in message_lower for word in ['заработал', 'получил', 'поступил']):
                return {"intent": "add_income", "confidence": 0.9}
        
        # Document-related intents
        doc_keywords = ['документ', 'договор', 'счет', 'акт', 'контракт']
        if any(kw in message_lower for kw in doc_keywords):
            if any(word in message_lower for word in ['создай', 'сгенерируй', 'подготовь']):
                return {"intent": "generate_document", "confidence": 0.85}
        
        # Marketing-related intents
        marketing_keywords = ['реклам', 'пост', 'кампани', 'маркетинг', 'продвиж']
        if any(kw in message_lower for kw in marketing_keywords):
            if any(word in message_lower for word in ['создай', 'запусти', 'новая']):
                return {"intent": "create_campaign", "confidence": 0.8}
            if any(word in message_lower for word in ['идеи', 'предложи', 'придумай']):
                return {"intent": "suggest_marketing_ideas", "confidence": 0.75}
        
        # General information intents
        if any(word in message_lower for word in ['как дела', 'статус', 'обзор', 'что нового']):
            return {"intent": "general_overview", "confidence": 0.7}
        
        # Default: conversational
        return {"intent": "conversation", "confidence": 0.6}

