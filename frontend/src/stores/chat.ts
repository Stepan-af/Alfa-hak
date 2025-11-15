/**
 * Chat store - AI Assistant conversations.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  ChatConversation,
  ChatConversationCreate,
  ChatConversationUpdate,
  ChatMessage,
  ChatMessageCreate,
  MessageFeedback,
  ChatStatistics,
  ChatBubble,
} from '@/types/chat'
import * as chatApi from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  // State
  const conversations = ref<ChatConversation[]>([])
  const activeConversation = ref<ChatConversation | null>(null)
  const messages = ref<ChatMessage[]>([])
  const statistics = ref<ChatStatistics | null>(null)
  const isLoading = ref(false)
  const isSending = ref(false)
  const error = ref<string | null>(null)
  const typingMessage = ref<string | null>(null)

  // Computed
  const activeConversations = computed(() =>
    conversations.value.filter((c) => !c.is_archived)
  )

  const archivedConversations = computed(() =>
    conversations.value.filter((c) => c.is_archived)
  )

  const chatBubbles = computed((): ChatBubble[] => {
    const bubbles: ChatBubble[] = [...messages.value]
    
    // Add typing indicator if AI is responding
    if (typingMessage.value) {
      bubbles.push({
        id: -1,
        conversation_id: activeConversation.value?.id || 0,
        role: 'assistant',
        content: typingMessage.value,
        created_at: new Date().toISOString(),
        isTyping: true,
      })
    }
    
    return bubbles
  })

  const hasActiveConversation = computed(() => activeConversation.value !== null)

  const lastMessage = computed(() => {
    if (messages.value.length === 0) return null
    return messages.value[messages.value.length - 1]
  })

  // Actions - Conversations
  async function fetchConversations(includeArchived = false) {
    isLoading.value = true
    error.value = null
    try {
      conversations.value = await chatApi.getConversations(includeArchived)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки бесед'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createConversation(data: ChatConversationCreate) {
    isLoading.value = true
    error.value = null
    try {
      const conversation = await chatApi.createConversation(data)
      conversations.value.unshift(conversation)
      activeConversation.value = conversation
      messages.value = []
      return conversation
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка создания беседы'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function selectConversation(id: number) {
    isLoading.value = true
    error.value = null
    try {
      const conversation = await chatApi.getConversation(id)
      activeConversation.value = conversation
      messages.value = conversation.messages || []
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки беседы'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function updateConversation(id: number, data: ChatConversationUpdate) {
    error.value = null
    try {
      const updated = await chatApi.updateConversation(id, data)
      const index = conversations.value.findIndex((c) => c.id === id)
      if (index !== -1) {
        conversations.value[index] = updated
      }
      if (activeConversation.value?.id === id) {
        activeConversation.value = updated
      }
      return updated
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка обновления беседы'
      throw err
    }
  }

  async function deleteConversation(id: number) {
    error.value = null
    try {
      await chatApi.deleteConversation(id)
      conversations.value = conversations.value.filter((c) => c.id !== id)
      if (activeConversation.value?.id === id) {
        activeConversation.value = null
        messages.value = []
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка удаления беседы'
      throw err
    }
  }

  async function archiveConversation(id: number) {
    return updateConversation(id, { is_archived: true })
  }

  async function unarchiveConversation(id: number) {
    return updateConversation(id, { is_archived: false })
  }

  // Actions - Messages
  async function sendMessage(content: string, conversationId?: number) {
    isSending.value = true
    error.value = null
    typingMessage.value = '💭 Думаю...'
    
    try {
      const data: ChatMessageCreate = {
        content,
        conversation_id: conversationId || activeConversation.value?.id,
      }
      
      // Send message and get AI response
      const aiMessage = await chatApi.sendMessage(data)
      
      // If new conversation was created, fetch it
      if (!conversationId && !activeConversation.value) {
        await fetchConversations()
        const newConv = conversations.value.find((c) => c.id === aiMessage.conversation_id)
        if (newConv) {
          activeConversation.value = newConv
        }
      }
      
      // Add user message (reconstruct from request)
      messages.value.push({
        id: messages.value.length + 1000, // Temp ID
        conversation_id: aiMessage.conversation_id,
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      })
      
      // Add AI message
      messages.value.push(aiMessage)
      
      // Update conversation timestamp
      if (activeConversation.value) {
        activeConversation.value.updated_at = aiMessage.created_at
      }
      
      return aiMessage
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка отправки сообщения'
      
      // Add error message
      messages.value.push({
        id: -2,
        conversation_id: activeConversation.value?.id || 0,
        role: 'assistant',
        content: 'Извините, произошла ошибка. Попробуйте еще раз.',
        created_at: new Date().toISOString(),
        isError: true,
      } as ChatBubble)
      
      throw err
    } finally {
      isSending.value = false
      typingMessage.value = null
    }
  }

  async function rateMessage(messageId: number, rating: number, feedback?: string) {
    error.value = null
    try {
      const data: MessageFeedback = { message_id: messageId, rating, feedback }
      const updated = await chatApi.rateMessage(data)
      
      // Update message in store
      const index = messages.value.findIndex((m) => m.id === messageId)
      if (index !== -1) {
        messages.value[index] = updated
      }
      
      return updated
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка оценки сообщения'
      throw err
    }
  }

  // Actions - Statistics
  async function fetchStatistics() {
    isLoading.value = true
    error.value = null
    try {
      statistics.value = await chatApi.getStatistics()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки статистики'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Utility
  function clearActiveConversation() {
    activeConversation.value = null
    messages.value = []
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    conversations,
    activeConversation,
    messages,
    statistics,
    isLoading,
    isSending,
    error,
    
    // Computed
    activeConversations,
    archivedConversations,
    chatBubbles,
    hasActiveConversation,
    lastMessage,
    
    // Actions
    fetchConversations,
    createConversation,
    selectConversation,
    updateConversation,
    deleteConversation,
    archiveConversation,
    unarchiveConversation,
    sendMessage,
    rateMessage,
    fetchStatistics,
    clearActiveConversation,
    clearError,
  }
})
