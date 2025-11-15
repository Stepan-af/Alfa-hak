<template>
  <v-container fluid class="chat-container pa-0">
    <v-row no-gutters style="height: calc(100vh - 64px)">
      <!-- Sidebar: Conversations List -->
      <v-col cols="12" md="3" class="chat-sidebar">
        <v-card class="h-100" elevation="0">
          <v-card-title class="d-flex align-center">
            <span class="text-h6">💬 Беседы</span>
            <v-spacer />
            <v-btn
              icon="mdi-plus"
              variant="text"
              size="small"
              @click="startNewConversation"
            />
          </v-card-title>
          <v-divider />
          
          <v-card-text class="pa-0">
            <v-list density="compact">
              <v-list-item
                v-for="conv in activeConversations"
                :key="conv.id"
                :active="activeConversation?.id === conv.id"
                @click="selectConversation(conv.id)"
              >
                <v-list-item-title>{{ conv.title }}</v-list-item-title>
                <v-list-item-subtitle>
                  {{ formatTimestamp(conv.updated_at) }}
                </v-list-item-subtitle>
                <template #append>
                  <v-menu>
                    <template #activator="{ props }">
                      <v-btn
                        icon="mdi-dots-vertical"
                        variant="text"
                        size="x-small"
                        v-bind="props"
                        @click.stop
                      />
                    </template>
                    <v-list>
                      <v-list-item @click="renameConversation(conv)">
                        <template #prepend>
                          <v-icon>mdi-pencil</v-icon>
                        </template>
                        <v-list-item-title>Переименовать</v-list-item-title>
                      </v-list-item>
                      <v-list-item @click="archiveConversationAction(conv.id)">
                        <template #prepend>
                          <v-icon>mdi-archive</v-icon>
                        </template>
                        <v-list-item-title>Архивировать</v-list-item-title>
                      </v-list-item>
                      <v-list-item @click="confirmDeleteConversation(conv.id)">
                        <template #prepend>
                          <v-icon color="error">mdi-delete</v-icon>
                        </template>
                        <v-list-item-title>Удалить</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </template>
              </v-list-item>

              <v-divider v-if="archivedConversations.length > 0" class="my-2" />
              
              <v-list-subheader v-if="archivedConversations.length > 0">
                Архив
              </v-list-subheader>
              <v-list-item
                v-for="conv in archivedConversations"
                :key="conv.id"
                @click="selectConversation(conv.id)"
              >
                <template #prepend>
                  <v-icon size="small">mdi-archive</v-icon>
                </template>
                <v-list-item-title>{{ conv.title }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Main Chat Area -->
      <v-col cols="12" md="9" class="chat-main">
        <v-card class="h-100 d-flex flex-column" elevation="0">
          <!-- Chat Header -->
          <v-card-title v-if="hasActiveConversation" class="d-flex align-center">
            <span>{{ activeConversation?.title }}</span>
            <v-spacer />
            <v-btn icon="mdi-information" variant="text" size="small" @click="showStatistics" />
          </v-card-title>
          <v-divider />

          <!-- Welcome Screen -->
          <v-card-text v-if="!hasActiveConversation" class="d-flex flex-column align-center justify-center flex-grow-1">
            <div class="text-center">
              <v-icon size="80" color="primary">mdi-robot-happy</v-icon>
              <h2 class="text-h4 mt-4 mb-2">Привет! Я ваш AI-помощник</h2>
              <p class="text-body-1 mb-6">Задайте любой вопрос о вашем бизнесе</p>
              
              <v-row justify="center">
                <v-col cols="12" sm="6" md="4">
                  <v-btn
                    block
                    color="primary"
                    prepend-icon="mdi-plus"
                    @click="startNewConversation"
                  >
                    Начать беседу
                  </v-btn>
                </v-col>
              </v-row>

              <v-divider class="my-6" />
              
              <div class="text-left" style="max-width: 600px">
                <h3 class="text-h6 mb-3">Примеры вопросов:</h3>
                <v-chip
                  v-for="(example, idx) in exampleQuestions"
                  :key="idx"
                  class="ma-1"
                  @click="askExample(example)"
                >
                  {{ example }}
                </v-chip>
              </div>
            </div>
          </v-card-text>

          <!-- Messages Area -->
          <v-card-text
            v-else
            ref="messagesContainer"
            class="messages-area flex-grow-1"
            style="overflow-y: auto; height: 0"
          >
            <!-- Quick Actions Component -->
            <QuickActions
              v-if="suggestedActions.length > 0"
              :actions="suggestedActions"
              :conversation-id="activeConversation?.id"
              @close="suggestedActions = []"
              @action-executed="onActionExecuted"
            />

            <div v-for="(bubble, idx) in chatBubbles" :key="idx" class="message-wrapper" :class="bubble.role">
              <div class="message-bubble" :class="{ typing: bubble.isTyping, error: bubble.isError }">
                <div class="message-avatar">
                  <v-icon v-if="bubble.role === 'user'" color="primary">mdi-account</v-icon>
                  <v-icon v-else color="success">mdi-robot</v-icon>
                </div>
                <div class="message-content">
                  <div class="message-text">{{ bubble.content }}</div>
                  <div class="message-meta">
                    <span class="message-time">{{ formatTime(bubble.created_at) }}</span>
                    <span v-if="bubble.tokens_used" class="message-tokens">
                      🪙 {{ bubble.tokens_used }} токенов
                    </span>
                  </div>
                  <!-- Rating for assistant messages -->
                  <div v-if="bubble.role === 'assistant' && !bubble.isTyping && bubble.id > 0" class="message-rating">
                    <v-rating
                      :model-value="bubble.user_rating || 0"
                      density="compact"
                      size="small"
                      hover
                      @update:model-value="(val) => rateMessageAction(bubble.id, Number(val))"
                    />
                  </div>
                </div>
              </div>
            </div>
          </v-card-text>

          <!-- Input Area -->
          <v-card-actions v-if="hasActiveConversation" class="chat-input pa-4">
            <v-textarea
              v-model="userInput"
              placeholder="Напишите сообщение..."
              rows="2"
              auto-grow
              variant="outlined"
              density="comfortable"
              :disabled="isSending"
              @keydown.enter.exact.prevent="sendUserMessage"
            />
            <v-btn
              icon="mdi-send"
              color="primary"
              :loading="isSending"
              :disabled="!userInput.trim() || isSending"
              @click="sendUserMessage"
            />
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Rename Dialog -->
    <v-dialog v-model="renameDialog" max-width="400px">
      <v-card>
        <v-card-title>Переименовать беседу</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="newConversationTitle"
            label="Название"
            density="comfortable"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="renameDialog = false">Отмена</v-btn>
          <v-btn color="primary" @click="saveConversationTitle">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Statistics Dialog -->
    <v-dialog v-model="statisticsDialog" max-width="500px">
      <v-card>
        <v-card-title>📊 Статистика чата</v-card-title>
        <v-card-text>
          <v-row v-if="statistics">
            <v-col cols="6">
              <div class="text-h4">{{ statistics.total_conversations }}</div>
              <div class="text-caption">Бесед</div>
            </v-col>
            <v-col cols="6">
              <div class="text-h4">{{ statistics.total_messages }}</div>
              <div class="text-caption">Сообщений</div>
            </v-col>
            <v-col cols="6">
              <div class="text-h4">{{ statistics.avg_messages_per_conversation.toFixed(1) }}</div>
              <div class="text-caption">Сообщений на беседу</div>
            </v-col>
            <v-col cols="6">
              <div class="text-h4">{{ statistics.total_tokens_used }}</div>
              <div class="text-caption">Токенов использовано</div>
            </v-col>
            <v-col v-if="statistics.most_used_model" cols="12">
              <v-chip size="small">🤖 {{ statistics.most_used_model }}</v-chip>
            </v-col>
            <v-col v-if="statistics.avg_user_rating" cols="12">
              <div>Средняя оценка:</div>
              <v-rating
                :model-value="statistics.avg_user_rating"
                readonly
                density="compact"
                size="small"
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="statisticsDialog = false">Закрыть</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { storeToRefs } from 'pinia'
import { useNotification } from '@/composables/useNotification'
import type { ChatConversation } from '@/types/chat'
import type { SuggestedAction } from '@/types/integration'
import { parseActions } from '@/api/integration'
import QuickActions from '@/components/QuickActions.vue'

const chatStore = useChatStore()
const {
  activeConversation,
  chatBubbles,
  statistics,
  hasActiveConversation,
  activeConversations,
  archivedConversations,
  isSending,
} = storeToRefs(chatStore)
const { show: showNotification } = useNotification()

// Local state
const userInput = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const renameDialog = ref(false)
const statisticsDialog = ref(false)
const suggestedActions = ref<SuggestedAction[]>([])
const conversationToRename = ref<ChatConversation | null>(null)
const newConversationTitle = ref('')

const exampleQuestions = [
  'Как дела с финансами за месяц?',
  'Какие задачи просрочены?',
  'Сгенерируй пост для Instagram',
  'Создай контракт с клиентом',
  'Подскажи идеи для маркетинга',
]

// Methods
const loadConversations = async () => {
  try {
    await chatStore.fetchConversations()
  } catch (error) {
    showNotification('Ошибка загрузки бесед', 'error')
  }
}

const startNewConversation = async () => {
  try {
    await chatStore.createConversation({ title: 'Новый разговор' })
  } catch (error) {
    showNotification('Ошибка создания беседы', 'error')
  }
}

const selectConversation = async (id: number) => {
  try {
    await chatStore.selectConversation(id)
    scrollToBottom()
  } catch (error) {
    showNotification('Ошибка загрузки беседы', 'error')
  }
}

const sendUserMessage = async () => {
  if (!userInput.value.trim() || isSending.value) return

  const message = userInput.value.trim()
  userInput.value = ''

  try {
    const aiMessage = await chatStore.sendMessage(message)
    
    // Parse AI response for suggested actions
    if (aiMessage && aiMessage.content) {
      try {
        const { actions } = await parseActions(aiMessage.content)
        if (actions && actions.length > 0) {
          suggestedActions.value = actions
        }
      } catch (parseError) {
        // Silent fail - actions are optional
        console.log('No actions found in response')
      }
    }
    
    await nextTick()
    scrollToBottom()
  } catch (error) {
    showNotification('Ошибка отправки сообщения', 'error')
  }
}

const onActionExecuted = async (result: any) => {
  // Reload relevant data after action execution
  showNotification('Действие выполнено! Обновляю данные...', 'info')
  suggestedActions.value = []
  
  // Send confirmation message to chat
  const confirmMessage = `✅ Действие выполнено успешно! ${JSON.stringify(result)}`
  await chatStore.sendMessage(confirmMessage)
}

const askExample = async (question: string) => {
  userInput.value = question
  if (!hasActiveConversation.value) {
    await startNewConversation()
  }
  await sendUserMessage()
}

const renameConversation = (conv: ChatConversation) => {
  conversationToRename.value = conv
  newConversationTitle.value = conv.title
  renameDialog.value = true
}

const saveConversationTitle = async () => {
  if (!conversationToRename.value || !newConversationTitle.value.trim()) return

  try {
    await chatStore.updateConversation(conversationToRename.value.id, {
      title: newConversationTitle.value.trim(),
    })
    renameDialog.value = false
    showNotification('Название обновлено', 'success')
  } catch (error) {
    showNotification('Ошибка переименования', 'error')
  }
}

const archiveConversationAction = async (id: number) => {
  try {
    await chatStore.archiveConversation(id)
    showNotification('Беседа архивирована', 'success')
  } catch (error) {
    showNotification('Ошибка архивации', 'error')
  }
}

const confirmDeleteConversation = async (id: number) => {
  if (confirm('Удалить беседу?')) {
    try {
      await chatStore.deleteConversation(id)
      showNotification('Беседа удалена', 'success')
    } catch (error) {
      showNotification('Ошибка удаления', 'error')
    }
  }
}

const rateMessageAction = async (messageId: number, rating: number) => {
  try {
    await chatStore.rateMessage(messageId, rating)
    showNotification('Спасибо за оценку!', 'success')
  } catch (error) {
    showNotification('Ошибка оценки', 'error')
  }
}

const showStatistics = async () => {
  try {
    await chatStore.fetchStatistics()
    statisticsDialog.value = true
  } catch (error) {
    showNotification('Ошибка загрузки статистики', 'error')
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const formatTimestamp = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return 'Сегодня'
  if (days === 1) return 'Вчера'
  if (days < 7) return `${days} дн. назад`
  return date.toLocaleDateString('ru-RU', { month: 'short', day: 'numeric' })
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Watch for new messages and scroll
watch(() => chatBubbles.value.length, () => {
  scrollToBottom()
})

onMounted(() => {
  loadConversations()
})
</script>

<style scoped>
.chat-container {
  height: calc(100vh - 64px);
}

.chat-sidebar {
  border-right: 1px solid rgba(255, 255, 255, 0.12);
}

.messages-area {
  background: var(--v-theme-background);
  padding: 16px;
}

.message-wrapper {
  margin-bottom: 16px;
  display: flex;
}

.message-wrapper.user {
  justify-content: flex-end;
}

.message-wrapper.assistant {
  justify-content: flex-start;
}

.message-bubble {
  display: flex;
  gap: 12px;
  max-width: 70%;
}

.message-wrapper.user .message-bubble {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--v-theme-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.message-content {
  flex: 1;
}

.message-text {
  background: var(--v-theme-surface);
  color: rgba(255, 255, 255, 0.87);
  padding: 12px 16px;
  border-radius: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  white-space: pre-wrap;
  word-break: break-word;
}

.message-wrapper.user .message-text {
  background: rgb(var(--v-theme-primary));
  color: white;
}

.message-bubble.typing .message-text {
  background: var(--v-theme-surface);
  color: rgb(var(--v-theme-info));
  font-style: italic;
}

.message-bubble.error .message-text {
  background: rgba(239, 68, 68, 0.1);
  color: rgb(var(--v-theme-error));
}

.message-meta {
  display: flex;
  gap: 12px;
  margin-top: 4px;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
}

.message-rating {
  margin-top: 8px;
}

.chat-input {
  border-top: 1px solid rgba(255, 255, 255, 0.12);
  background: var(--v-theme-surface);
}

/* Ensure textarea has proper text color */
.chat-input :deep(.v-field) {
  color: rgba(255, 255, 255, 0.87);
}

.chat-input :deep(.v-field__input) {
  color: rgba(255, 255, 255, 0.87);
}

.chat-input :deep(.v-field--variant-outlined .v-field__outline) {
  color: rgba(255, 255, 255, 0.38);
}

.chat-input :deep(textarea::placeholder) {
  color: rgba(255, 255, 255, 0.5);
  opacity: 1;
}
</style>
