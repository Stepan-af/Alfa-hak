/**
 * Chat module types.
 */

export interface ChatMessage {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
  tokens_used?: number
  model_used?: string
  user_rating?: number
}

export interface ChatMessageWithContext extends ChatMessage {
  context_documents?: number[]
  context_tasks?: number[]
  context_finance?: number[]
  context_marketing?: number[]
}

export interface ChatMessageCreate {
  content: string
  conversation_id?: number  // If null, creates new conversation
}

export interface ChatConversation {
  id: number
  user_id: number
  title: string
  created_at: string
  updated_at: string
  is_archived: boolean
  metadata?: Record<string, any>
}

export interface ChatConversationWithMessages extends ChatConversation {
  messages: ChatMessage[]
}

export interface ChatConversationCreate {
  title?: string
  metadata?: Record<string, any>
}

export interface ChatConversationUpdate {
  title?: string
  is_archived?: boolean
  metadata?: Record<string, any>
}

export interface MessageFeedback {
  message_id: number
  rating: number  // 1-5
  feedback?: string
}

export interface ChatStatistics {
  total_conversations: number
  total_messages: number
  avg_messages_per_conversation: number
  total_tokens_used: number
  most_used_model?: string
  avg_user_rating?: number
}

// UI Helper types
export interface ChatBubble extends ChatMessage {
  isTyping?: boolean
  isError?: boolean
}

export const MESSAGE_ROLES = {
  USER: 'user' as const,
  ASSISTANT: 'assistant' as const,
}

export const RATING_OPTIONS = [
  { value: 1, label: '1 ⭐', icon: 'mdi-star-outline' },
  { value: 2, label: '2 ⭐⭐', icon: 'mdi-star-half-full' },
  { value: 3, label: '3 ⭐⭐⭐', icon: 'mdi-star' },
  { value: 4, label: '4 ⭐⭐⭐⭐', icon: 'mdi-star' },
  { value: 5, label: '5 ⭐⭐⭐⭐⭐', icon: 'mdi-star' },
]
