/**
 * Integration API - Search and Actions.
 */
import apiClient from './client'
import type {
  SearchResults,
  SearchResult,
  SuggestedAction,
  ActionExecutionResult,
  RecentActivity,
} from '@/types/integration'

const SEARCH_URL = '/search'
const CHAT_URL = '/api/v1/chat'

// ============= Search =============

export async function searchAll(query: string, limit = 50): Promise<SearchResults> {
  const response = await apiClient.get(`${SEARCH_URL}/search`, {
    params: { q: query, limit },
  })
  return response.data
}

export async function searchByType(
  type: string,
  query: string,
  limit = 50
): Promise<{ type: string; results: SearchResult[] }> {
  const response = await apiClient.get(`${SEARCH_URL}/search/${type}`, {
    params: { q: query, limit },
  })
  return response.data
}

export async function getRecentActivity(days = 7, limit = 20): Promise<RecentActivity> {
  const response = await apiClient.get(`${SEARCH_URL}/recent`, {
    params: { days, limit },
  })
  return response.data
}

// ============= Actions =============

export async function executeAction(
  action: SuggestedAction,
  conversationId: number
): Promise<ActionExecutionResult> {
  const response = await apiClient.post(`${CHAT_URL}/actions/execute`, {
    action,
    conversation_id: conversationId,
  })
  return response.data
}

export async function parseActions(aiResponse: string): Promise<{ actions: SuggestedAction[] }> {
  const response = await apiClient.post(`${CHAT_URL}/actions/parse`, null, {
    params: { ai_response: aiResponse },
  })
  return response.data
}

export async function detectIntent(message: string): Promise<{ intent: string; confidence: number }> {
  const response = await apiClient.post(`${CHAT_URL}/intent/detect`, null, {
    params: { message },
  })
  return response.data
}
