<template>
  <div
    ref="messageRef"
    :class="['chat-message', `chat-message--${message.role}`, { 'chat-message--animated': animated }]"
  >
    <div class="chat-message__avatar">
      <v-avatar :color="avatarColor" size="36">
        <v-icon :icon="avatarIcon" size="20" />
      </v-avatar>
    </div>

    <div class="chat-message__content">
      <div class="chat-message__header">
        <span class="chat-message__author">{{ authorName }}</span>
        <span class="chat-message__time">{{ formattedTime }}</span>
      </div>

      <div class="chat-message__text">
        <div v-if="message.role === 'assistant' && isTyping" class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <div v-else v-html="formattedContent"></div>
      </div>

      <div v-if="message.role === 'assistant' && !isTyping" class="chat-message__actions">
        <v-btn
          size="x-small"
          variant="text"
          icon="mdi-thumb-up-outline"
          @click="$emit('feedback', 1)"
        />
        <v-btn
          size="x-small"
          variant="text"
          icon="mdi-thumb-down-outline"
          @click="$emit('feedback', -1)"
        />
        <v-btn
          size="x-small"
          variant="text"
          icon="mdi-content-copy"
          @click="copyMessage"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCardEnterAnimation } from '@/composables/useAnimations'

interface Message {
  id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

interface Props {
  message: Message
  isTyping?: boolean
  animated?: boolean
  delay?: number
}

const props = withDefaults(defineProps<Props>(), {
  isTyping: false,
  animated: true,
  delay: 0
})

defineEmits<{
  feedback: [rating: number]
}>()

const messageRef = ref<HTMLElement | null>(null)

// Анимация появления сообщения
if (props.animated) {
  useCardEnterAnimation(messageRef, props.delay)
}

const avatarColor = computed(() => {
  return props.message.role === 'user' ? 'primary' : 'success'
})

const avatarIcon = computed(() => {
  return props.message.role === 'user' ? 'mdi-account' : 'mdi-robot'
})

const authorName = computed(() => {
  return props.message.role === 'user' ? 'Вы' : 'AI Помощник'
})

const formattedTime = computed(() => {
  const date = new Date(props.message.created_at)
  return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
})

const formattedContent = computed(() => {
  if (!props.message.content) return ''
  
  // Простое форматирование без markdown библиотеки
  return props.message.content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
})

const copyMessage = async () => {
  try {
    await navigator.clipboard.writeText(props.message.content)
    // Можно добавить toast notification
  } catch (e) {
    console.error('Failed to copy:', e)
  }
}
</script>

<style scoped>
.chat-message {
  display: flex;
  gap: 12px;
  padding: 16px;
  margin-bottom: 16px;
  border-radius: 12px;
  transition: background-color 0.2s;
}

.chat-message--animated {
  animation: slideInFromLeft 0.3s ease-out;
}

.chat-message--user {
  flex-direction: row-reverse;
  background: rgba(239, 49, 36, 0.05);
}

.chat-message--user .chat-message__content {
  align-items: flex-end;
}

.chat-message--assistant {
  background: rgba(76, 175, 80, 0.05);
}

.chat-message:hover {
  background-color: rgba(255, 255, 255, 0.03);
}

.chat-message__avatar {
  flex-shrink: 0;
}

.chat-message__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.chat-message__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.chat-message__author {
  font-weight: 600;
  font-size: 14px;
}

.chat-message__time {
  font-size: 12px;
  opacity: 0.6;
}

.chat-message__text {
  font-size: 15px;
  line-height: 1.6;
  word-wrap: break-word;
}

.chat-message__text :deep(p) {
  margin: 0 0 8px 0;
}

.chat-message__text :deep(p:last-child) {
  margin-bottom: 0;
}

.chat-message__text :deep(code) {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.chat-message__text :deep(pre) {
  background: rgba(0, 0, 0, 0.3);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}

.chat-message__text :deep(pre code) {
  background: none;
  padding: 0;
}

.chat-message__actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.chat-message:hover .chat-message__actions {
  opacity: 1;
}

/* Typing indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: currentColor;
  border-radius: 50%;
  opacity: 0.4;
  animation: typingBounce 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typingBounce {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}

@keyframes slideInFromLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .chat-message {
    padding: 12px;
  }
  
  .chat-message__text {
    font-size: 14px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .chat-message--animated {
    animation: none;
  }
  
  .typing-indicator span {
    animation: none;
  }
}
</style>
