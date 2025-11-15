<template>
  <v-btn
    ref="buttonRef"
    :color="color"
    :variant="variant"
    :size="size"
    :loading="loading"
    :disabled="disabled"
    :block="block"
    :rounded="rounded"
    class="action-button"
    :class="buttonClasses"
    @click="handleClick"
  >
    <v-icon v-if="icon || prependIcon" :icon="icon || prependIcon" start></v-icon>
    <slot>{{ label }}</slot>
    <v-icon v-if="appendIcon" :icon="appendIcon" end></v-icon>
  </v-btn>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useHoverEffect } from '@/composables/useAnimations'

interface Props {
  label?: string
  icon?: string
  color?: string
  variant?: 'flat' | 'text' | 'elevated' | 'tonal' | 'outlined' | 'plain'
  size?: 'x-small' | 'small' | 'default' | 'large' | 'x-large'
  loading?: boolean
  disabled?: boolean
  block?: boolean
  rounded?: string | number | boolean
  prependIcon?: string
  appendIcon?: string
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  color: 'primary',
  variant: 'flat',
  size: 'default',
  loading: false,
  disabled: false,
  block: false,
  rounded: 'lg',
  animated: true
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonRef = ref<HTMLElement | null>(null)

// Применяем hover эффект если анимация включена
if (props.animated) {
  useHoverEffect(buttonRef)
}

const buttonClasses = computed(() => ({
  'action-button--animated': props.animated,
  'action-button--loading': props.loading
}))

const handleClick = (event: MouseEvent) => {
  if (!props.loading && !props.disabled) {
    emit('click', event)
  }
}
</script>

<style scoped>
.action-button {
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: none;
  transition: box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
}

.action-button--animated:not(.action-button--loading):hover {
  box-shadow: 0 8px 16px rgba(239, 49, 36, 0.3);
}

.action-button--animated:not(.action-button--loading):active {
  box-shadow: 0 4px 8px rgba(239, 49, 36, 0.2);
}

.action-button :deep(.v-btn__content) {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
