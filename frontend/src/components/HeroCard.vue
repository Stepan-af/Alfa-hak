<template>
  <v-card
    :to="to"
    :href="href"
    class="hero-card"
    :class="cardClasses"
    :style="cardStyle"
    elevation="4"
    rounded="xl"
  >
    <div class="hero-card__gradient"></div>
    
    <v-card-text class="hero-card__content pa-8">
      <div class="hero-card__header mb-6">
        <v-icon
          v-if="icon"
          :icon="icon"
          size="56"
          class="hero-card__icon mb-4"
        ></v-icon>
        <h2 class="hero-card__title text-h4 font-weight-bold mb-2">
          {{ title }}
        </h2>
        <p v-if="subtitle" class="hero-card__subtitle text-h6 text-medium-emphasis">
          {{ subtitle }}
        </p>
      </div>

      <div class="hero-card__body mb-6">
        <p class="text-body-1">
          <slot>{{ description }}</slot>
        </p>
      </div>

      <div v-if="$slots.actions || action" class="hero-card__actions">
        <slot name="actions">
          <ActionButton
            v-if="action"
            :color="actionColor"
            :prepend-icon="actionIcon"
            size="large"
          >
            {{ action }}
          </ActionButton>
        </slot>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ActionButton from './ActionButton.vue'

interface Props {
  title: string
  subtitle?: string
  description?: string
  icon?: string
  gradientFrom?: string
  gradientTo?: string
  to?: string
  href?: string
  action?: string
  actionIcon?: string
  actionColor?: string
  animated?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  gradientFrom: '#ef3124',
  gradientTo: '#ff6b58',
  actionColor: 'primary',
  animated: true
})

const cardClasses = computed(() => ({
  'hero-card--animated': props.animated,
  'hero-card--clickable': props.to || props.href
}))

const cardStyle = computed(() => ({
  '--gradient-from': props.gradientFrom,
  '--gradient-to': props.gradientTo
}))
</script>

<style scoped>
.hero-card {
  position: relative;
  overflow: hidden;
  height: 100%;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.hero-card__gradient {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(
    135deg,
    var(--gradient-from) 0%,
    var(--gradient-to) 100%
  );
  opacity: 0.15;
  transition: opacity 0.4s ease;
}

.hero-card--animated:hover .hero-card__gradient {
  opacity: 0.25;
}

.hero-card__content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.hero-card__icon {
  color: var(--gradient-from);
  filter: drop-shadow(0 4px 8px rgba(239, 49, 36, 0.3));
}

.hero-card__title {
  background: linear-gradient(
    135deg,
    var(--gradient-from) 0%,
    var(--gradient-to) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-card__subtitle {
  opacity: 0.8;
}

.hero-card__body {
  flex: 1;
  opacity: 0.9;
}

.hero-card__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.hero-card--animated.hero-card--clickable:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(239, 49, 36, 0.3) !important;
  border-color: var(--gradient-from);
}

.hero-card--animated:not(.hero-card--clickable):hover {
  transform: translateY(-4px);
}
</style>
