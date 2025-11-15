<template>
  <v-card
    class="stat-widget"
    :class="{ 'stat-widget--animated': animated }"
    elevation="2"
    rounded="lg"
  >
    <v-card-text class="pa-6">
      <div class="stat-header mb-4">
        <v-icon
          v-if="icon"
          :icon="icon"
          :color="iconColor"
          size="40"
          class="stat-icon"
        ></v-icon>
        <div class="stat-trend" v-if="trend">
          <v-chip
            :color="trendColor"
            size="small"
            variant="tonal"
          >
            <v-icon :icon="trendIcon" start size="small"></v-icon>
            {{ trend }}
          </v-chip>
        </div>
      </div>

      <div class="stat-content">
        <h3 class="stat-value text-h3 font-weight-bold mb-2">
          {{ formattedValue }}
        </h3>
        <p class="stat-label text-body-2 text-medium-emphasis">
          {{ label }}
        </p>
        <p v-if="description" class="stat-description text-caption text-medium-emphasis mt-2">
          {{ description }}
        </p>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  value: number | string
  label: string
  description?: string
  icon?: string
  iconColor?: string
  trend?: string
  trendDirection?: 'up' | 'down' | 'neutral'
  format?: 'number' | 'currency' | 'percent' | 'custom'
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: 'primary',
  trendDirection: 'neutral',
  format: 'number',
  animated: true
})

const formattedValue = computed(() => {
  if (typeof props.value === 'string') {
    return props.value
  }

  switch (props.format) {
    case 'currency':
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
      }).format(props.value)
    case 'percent':
      return `${props.value}%`
    case 'number':
      return new Intl.NumberFormat('ru-RU').format(props.value)
    default:
      return props.value
  }
})

const trendColor = computed(() => {
  switch (props.trendDirection) {
    case 'up':
      return 'success'
    case 'down':
      return 'error'
    default:
      return 'info'
  }
})

const trendIcon = computed(() => {
  switch (props.trendDirection) {
    case 'up':
      return 'mdi-trending-up'
    case 'down':
      return 'mdi-trending-down'
    default:
      return 'mdi-minus'
  }
})
</script>

<style scoped>
.stat-widget {
  height: 100%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-widget--animated:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3) !important;
  border-color: var(--v-theme-primary);
}

.stat-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.stat-icon {
  opacity: 0.9;
}

.stat-trend {
  display: flex;
  align-items: center;
}

.stat-value {
  color: rgba(255, 255, 255, 0.95);
  font-weight: 700;
}

.stat-label {
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-description {
  opacity: 0.7;
}
</style>
