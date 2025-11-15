/**
 * Chat API client.
 */
import apiClient from './client'
import type {
  ChatConversation,
  ChatConversationCreate,
  ChatConversationUpdate,
  ChatConversationWithMessages,
  ChatMessage,
  ChatMessageCreate,
  MessageFeedback,
  ChatStatistics,
} from '@/types/chat'

const API_URL = '/chat'

// ============= Conversations =============

export async function createConversation(data: ChatConversationCreate): Promise<ChatConversation> {
  const response = await apiClient.post(`${API_URL}/conversations`, data)
  return response.data
}

export async function getConversations(includeArchived = false): Promise<ChatConversation[]> {
  const response = await apiClient.get(`${API_URL}/conversations`, {
    params: { include_archived: includeArchived },
  })
  return response.data
}

export async function getConversation(id: number): Promise<ChatConversationWithMessages> {
  const response = await apiClient.get(`${API_URL}/conversations/${id}`)
  return response.data
}

export async function updateConversation(
  id: number,
  data: ChatConversationUpdate
): Promise<ChatConversation> {
  const response = await apiClient.put(`${API_URL}/conversations/${id}`, data)
  return response.data
}

export async function deleteConversation(id: number): Promise<void> {
  await apiClient.delete(`${API_URL}/conversations/${id}`)
}

// ============= Messages =============

export async function sendMessage(data: ChatMessageCreate): Promise<ChatMessage> {
  const response = await apiClient.post(`${API_URL}/messages`, data)
  return response.data
}

export async function getMessages(conversationId: number): Promise<ChatMessage[]> {
  const response = await apiClient.get(`${API_URL}/conversations/${conversationId}/messages`)
  return response.data
}

export async function rateMessage(data: MessageFeedback): Promise<ChatMessage> {
  const response = await apiClient.post(`${API_URL}/messages/${data.message_id}/feedback`, data)
  return response.data
}

// ============= Statistics =============

export async function getStatistics(): Promise<ChatStatistics> {
  const response = await apiClient.get(`${API_URL}/statistics`)
  return response.data
}
