<template>
  <v-card v-if="actions.length > 0" class="quick-actions-card" elevation="2">
    <v-card-title class="d-flex align-center">
      <v-icon color="primary" class="mr-2">mdi-lightning-bolt</v-icon>
      <span>Предлагаемые действия</span>
      <v-spacer />
      <v-btn icon="mdi-close" variant="text" size="small" @click="$emit('close')" />
    </v-card-title>
    <v-card-text>
      <v-list density="compact">
        <v-list-item
          v-for="(action, idx) in actions"
          :key="idx"
          class="action-item"
          @click="executeAction(action)"
        >
          <template #prepend>
            <v-avatar :color="getActionColor(action.type)" size="small">
              <v-icon :icon="getActionIcon(action.type)" size="small" />
            </v-avatar>
          </template>
          
          <v-list-item-title>{{ action.title }}</v-list-item-title>
          <v-list-item-subtitle>{{ action.description }}</v-list-item-subtitle>
          
          <template #append>
            <v-chip size="x-small" :color="getConfidenceColor(action.confidence)">
              {{ Math.round(action.confidence * 100) }}%
            </v-chip>
            <v-btn
              icon="mdi-play"
              variant="text"
              size="small"
              :loading="executingIndex === idx"
              @click.stop="executeAction(action)"
            />
          </template>
        </v-list-item>
      </v-list>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { SuggestedAction } from '@/types/integration'
import { ACTION_ICONS, ACTION_COLORS } from '@/types/integration'
import { executeAction as executeActionApi } from '@/api/integration'
import { useNotification } from '@/composables/useNotification'

interface Props {
  actions: SuggestedAction[]
  conversationId?: number
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'actionExecuted', result: any): void
}>()

const { show: showNotification } = useNotification()
const executingIndex = ref<number | null>(null)

const executeAction = async (action: SuggestedAction) => {
  if (!props.conversationId) {
    showNotification('Ошибка: нет активной беседы', 'error')
    return
  }

  executingIndex.value = props.actions.indexOf(action)
  
  try {
    const result = await executeActionApi(action, props.conversationId)
    
    if (result.success) {
      showNotification(result.message, 'success')
      emit('actionExecuted', result.data)
    } else {
      showNotification(result.message, 'error')
    }
  } catch (error: any) {
    showNotification(error.response?.data?.detail || 'Ошибка выполнения действия', 'error')
  } finally {
    executingIndex.value = null
  }
}

const getActionIcon = (type: string): string => {
  return ACTION_ICONS[type] || 'mdi-cog'
}

const getActionColor = (type: string): string => {
  return ACTION_COLORS[type] || 'grey'
}

const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return 'success'
  if (confidence >= 0.6) return 'warning'
  return 'error'
}
</script>

<style scoped>
.quick-actions-card {
  margin-bottom: 16px;
  border-left: 4px solid rgb(var(--v-theme-primary));
}

.action-item {
  cursor: pointer;
  transition: background-color 0.2s;
}

.action-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}
</style>