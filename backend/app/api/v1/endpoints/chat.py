"""
Chat endpoints for AI assistant.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db_sync
from app.auth import get_current_user
from app.models.user import User
from app.schemas.chat import (
    ChatConversation, ChatConversationCreate, ChatConversationUpdate, ChatConversationWithMessages,
    ChatMessage, ChatMessageCreate, ChatMessageWithContext,
    MessageFeedbackCreate, ChatStatistics
)
from app.services.chat_service import ChatService

router = APIRouter()


# ============= Conversation Endpoints =============

@router.post("/conversations", response_model=ChatConversation, status_code=status.HTTP_201_CREATED)
def create_conversation(
    data: ChatConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Create a new conversation."""
    service = ChatService(db)
    return service.create_conversation(current_user.id, data)


@router.get("/conversations", response_model=List[ChatConversation])
def get_conversations(
    include_archived: bool = False,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Get user's conversations."""
    service = ChatService(db)
    return service.get_conversations(current_user.id, include_archived, skip, limit)


@router.get("/conversations/{conversation_id}", response_model=ChatConversationWithMessages)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Get conversation with messages."""
    service = ChatService(db)
    conversation = service.get_conversation(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.put("/conversations/{conversation_id}", response_model=ChatConversation)
def update_conversation(
    conversation_id: int,
    data: ChatConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Update conversation (title, archive status)."""
    service = ChatService(db)
    conversation = service.update_conversation(conversation_id, current_user.id, data)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Delete conversation."""
    service = ChatService(db)
    if not service.delete_conversation(conversation_id, current_user.id):
        raise HTTPException(status_code=404, detail="Conversation not found")


# ============= Message Endpoints =============

@router.post("/messages", response_model=ChatMessage)
async def send_message(
    data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Send message to AI assistant."""
    service = ChatService(db)
    try:
        return await service.send_message(current_user.id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/conversations/{conversation_id}/messages", response_model=List[ChatMessage])
def get_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Get conversation messages."""
    service = ChatService(db)
    return service.get_messages(conversation_id, current_user.id, skip, limit)


@router.post("/messages/{message_id}/feedback", response_model=ChatMessage)
def rate_message(
    message_id: int,
    data: MessageFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Rate an assistant message."""
    service = ChatService(db)
    message = service.rate_message(message_id, current_user.id, data.rating, data.feedback)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


# ============= Analytics Endpoints =============

@router.get("/statistics", response_model=ChatStatistics)
def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Get chat statistics."""
    service = ChatService(db)
    return service.get_statistics(current_user.id)


# ============= Action Execution Endpoints =============

from app.schemas.chat import ActionExecutionRequest, ActionExecutionResult, SuggestedAction
from app.services.action_executor import ActionExecutor


@router.post("/actions/execute", response_model=ActionExecutionResult)
async def execute_action(
    request: ActionExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Execute a suggested action from AI assistant."""
    executor = ActionExecutor(db)
    
    result = executor.execute_action(
        user_id=current_user.id,
        action_type=request.action.type,
        parameters=request.action.parameters
    )
    
    return ActionExecutionResult(**result)


@router.post("/actions/parse")
async def parse_actions(
    ai_response: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Parse suggested actions from AI response."""
    service = ChatService(db)
    actions = service.parse_suggested_actions(ai_response)
    return {"actions": actions}


@router.post("/intent/detect")
async def detect_intent(
    message: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_sync)
):
    """Detect user intent from message."""
    service = ChatService(db)
    intent = service.detect_intent(message)
    return intent

