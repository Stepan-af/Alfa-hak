<template>
  <v-card
    ref="cardRef"
    :class="['stat-card', `stat-card--${color}`, { 'stat-card--clickable': clickable }]"
    :elevation="elevation"
    @click="handleClick"
  >
    <v-card-text class="stat-card__content">
      <div class="stat-card__header">
        <v-icon :icon="icon" :color="iconColor" size="32" class="stat-card__icon" />
        <v-chip v-if="trend" :color="trendColor" size="small" variant="flat" class="stat-card__trend">
          <v-icon :icon="trendIcon" size="14" start />
          {{ trend }}
        </v-chip>
      </div>

      <div class="stat-card__body">
        <div class="stat-card__value">{{ formattedValue }}</div>
        <div class="stat-card__label">{{ label }}</div>
      </div>

      <div v-if="subtitle" class="stat-card__subtitle">
        {{ subtitle }}
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useCardEnterAnimation, useHoverEffect, useCounterAnimation } from '@/composables/useAnimations'

interface Props {
  label: string
  value: number | string
  icon: string
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info'
  iconColor?: string
  subtitle?: string
  trend?: string
  trendDirection?: 'up' | 'down' | 'neutral'
  elevation?: number
  clickable?: boolean
  delay?: number
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  color: 'primary',
  elevation: 2,
  clickable: false,
  delay: 0,
  animated: true
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const cardRef = ref<HTMLElement | null>(null)

// Анимация появления карточки
if (props.animated) {
  useCardEnterAnimation(cardRef, props.delay)
  useHoverEffect(cardRef)
}

// Анимированный счетчик для числовых значений
const { displayValue, animate } = useCounterAnimation()

// Запускаем анимацию счетчика при изменении значения
watch(() => props.value, (newVal) => {
  const num = typeof newVal === 'string' ? parseFloat(newVal) : newVal
  if (!isNaN(num) && props.animated) {
    animate(num)
  } else {
    displayValue.value = num
  }
}, { immediate: true })

const formattedValue = computed(() => {
  if (typeof props.value === 'string' && isNaN(parseFloat(props.value))) {
    return props.value
  }
  return displayValue.value.toLocaleString('ru-RU')
})

const trendColor = computed(() => {
  switch (props.trendDirection) {
    case 'up': return 'success'
    case 'down': return 'error'
    default: return 'grey'
  }
})

const trendIcon = computed(() => {
  switch (props.trendDirection) {
    case 'up': return 'mdi-trending-up'
    case 'down': return 'mdi-trending-down'
    default: return 'mdi-minus'
  }
})

const handleClick = (event: MouseEvent) => {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style scoped>
.stat-card {
  border-radius: 16px;
  overflow: hidden;
  transition: box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
}

.stat-card--clickable {
  cursor: pointer;
}

.stat-card--primary {
  background: linear-gradient(135deg, rgba(239, 49, 36, 0.1) 0%, rgba(239, 49, 36, 0.05) 100%);
}

.stat-card--success {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
}

.stat-card--warning {
  background: linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%);
}

.stat-card--error {
  background: linear-gradient(135deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%);
}

.stat-card--info {
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(33, 150, 243, 0.05) 100%);
}

.stat-card__content {
  padding: 24px !important;
}

.stat-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.stat-card__icon {
  opacity: 0.9;
}

.stat-card__trend {
  font-weight: 600;
  font-size: 12px;
}

.stat-card__body {
  margin-bottom: 8px;
}

.stat-card__value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 4px;
  color: rgb(var(--v-theme-on-surface));
}

.stat-card__label {
  font-size: 14px;
  font-weight: 500;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-card__subtitle {
  font-size: 13px;
  opacity: 0.6;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Responsive */
@media (max-width: 768px) {
  .stat-card__value {
    font-size: 28px;
  }
  
  .stat-card__content {
    padding: 20px !important;
  }
}
</style>
