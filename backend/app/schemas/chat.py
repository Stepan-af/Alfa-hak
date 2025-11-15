"""
Chat schemas for AI assistant.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


# ============= Chat Message Schemas =============

class ChatMessageBase(BaseModel):
    """Base chat message schema."""
    content: str = Field(..., min_length=1, max_length=10000)


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a chat message."""
    conversation_id: Optional[int] = None  # If None, creates new conversation
    

class ChatMessage(ChatMessageBase):
    """Chat message response schema."""
    id: int
    conversation_id: int
    role: str  # 'user' or 'assistant'
    created_at: datetime
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None
    user_rating: Optional[int] = None
    
    class Config:
        from_attributes = True


class ChatMessageWithContext(ChatMessage):
    """Chat message with RAG context."""
    context_documents: Optional[List[int]] = None
    context_tasks: Optional[List[int]] = None
    context_finance: Optional[List[int]] = None
    context_marketing: Optional[List[int]] = None
    
    class Config:
        from_attributes = True


# ============= Chat Conversation Schemas =============

class ChatConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    title: Optional[str] = "Новый разговор"
    metadata: Optional[Dict[str, Any]] = None


class ChatConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    title: Optional[str] = None
    is_archived: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatConversation(BaseModel):
    """Chat conversation response schema."""
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    metadata_: Optional[Dict[str, Any]] = Field(None, serialization_alias='metadata')
    
    class Config:
        from_attributes = True
        populate_by_name = True


class ChatConversationWithMessages(ChatConversation):
    """Conversation with message history."""
    messages: List[ChatMessage] = []
    
    class Config:
        from_attributes = True


# ============= AI Response Schemas =============

class AIResponse(BaseModel):
    """AI assistant response."""
    message: ChatMessage
    suggestions: Optional[List[str]] = None  # Quick action suggestions
    confidence: Optional[float] = None  # 0.0 to 1.0


class StreamChunk(BaseModel):
    """Streaming response chunk."""
    content: str
    is_final: bool = False
    

# ============= Context Retrieval Schemas =============

class ContextDocument(BaseModel):
    """Document context for RAG."""
    id: int
    title: str
    content: str
    relevance_score: float


class ContextTask(BaseModel):
    """Task context for RAG."""
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    relevance_score: float


class ContextFinance(BaseModel):
    """Finance record context for RAG."""
    id: int
    description: str
    amount: float
    type: str
    category: str
    date: datetime
    relevance_score: float


class ContextMarketing(BaseModel):
    """Marketing campaign context for RAG."""
    id: int
    name: str
    description: Optional[str] = None
    platform: str
    status: str
    relevance_score: float


class RAGContext(BaseModel):
    """Full RAG context used for message generation."""
    documents: List[ContextDocument] = []
    tasks: List[ContextTask] = []
    finance: List[ContextFinance] = []
    marketing: List[ContextMarketing] = []
    user_profile: Optional[Dict[str, Any]] = None


# ============= Chat Analytics Schemas =============

class ChatStatistics(BaseModel):
    """Chat usage statistics."""
    total_conversations: int
    total_messages: int
    avg_messages_per_conversation: float
    total_tokens_used: int
    most_used_model: Optional[str] = None
    avg_user_rating: Optional[float] = None


class MessageFeedbackCreate(BaseModel):
    """Schema for message feedback."""
    message_id: int
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None


# ============= Action Schemas =============

class SuggestedAction(BaseModel):
    """AI-suggested action based on conversation."""
    type: str  # 'create_task', 'analyze_finance', 'generate_document', etc.
    title: str
    description: str
    parameters: Dict[str, Any]
    confidence: float


class ActionExecutionRequest(BaseModel):
    """Request to execute suggested action."""
    action: SuggestedAction
    conversation_id: int


class ActionExecutionResult(BaseModel):
    """Result of action execution."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
