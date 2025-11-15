"""
Chat models for AI assistant conversations.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.database import Base


class ChatConversation(Base):
    """Chat conversation model."""
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False, default="Новый разговор")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_archived = Column(Boolean, default=False)
    metadata_ = Column("metadata", JSONB, nullable=True)  # Store additional context
    
    # Relationships
    user = relationship("User", back_populates="chat_conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

    def __repr__(self):
        return f"<ChatConversation(id={self.id}, title={self.title})>"


class ChatMessage(Base):
    """Chat message model with vector embeddings."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Vector embedding for semantic search (pgvector)
    embedding = Column(Vector(384), nullable=True)  # all-MiniLM-L6-v2 produces 384-dim vectors
    
    # AI metadata
    tokens_used = Column(Integer, nullable=True)
    model_used = Column(String(100), nullable=True)  # e.g., "qwen2.5:7b", "gpt-4"
    
    # Context used for RAG (Retrieval-Augmented Generation)
    context_documents = Column(JSONB, nullable=True)  # IDs of documents used
    context_tasks = Column(JSONB, nullable=True)  # IDs of tasks referenced
    context_finance = Column(JSONB, nullable=True)  # IDs of finance records referenced
    context_marketing = Column(JSONB, nullable=True)  # IDs of marketing campaigns referenced
    
    # Feedback
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    user_feedback = Column(Text, nullable=True)
    
    # Relationships
    conversation = relationship("ChatConversation", back_populates="messages")

    def __repr__(self):
        preview = self.content[:50] if self.content else ""
        return f"<ChatMessage(id={self.id}, role={self.role}, content='{preview}...')>"
