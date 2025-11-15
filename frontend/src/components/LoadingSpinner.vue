<template>
  <div class="loading-spinner" :class="sizeClass">
    <div class="spinner-container">
      <v-progress-circular
        :indeterminate="true"
        :size="spinnerSize"
        :width="spinnerWidth"
        :color="color"
      ></v-progress-circular>
      <p v-if="message" class="loading-message mt-4">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'small' | 'medium' | 'large'
  color?: string
  message?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  color: 'primary',
  message: ''
})

const sizeClass = computed(() => `spinner-${props.size}`)

const spinnerSize = computed(() => {
  switch (props.size) {
    case 'small':
      return 32
    case 'large':
      return 80
    default:
      return 56
  }
})

const spinnerWidth = computed(() => {
  switch (props.size) {
    case 'small':
      return 3
    case 'large':
      return 6
    default:
      return 4
  }
})
</script>

<style scoped>
.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-message {
  font-size: 0.875rem;
  color: var(--v-theme-on-surface);
  opacity: 0.7;
  text-align: center;
}

.spinner-small .loading-message {
  font-size: 0.75rem;
  margin-top: 8px;
}

.spinner-large .loading-message {
  font-size: 1rem;
  margin-top: 16px;
}
</style>
