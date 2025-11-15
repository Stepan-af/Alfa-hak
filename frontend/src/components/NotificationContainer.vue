<template>
  <teleport to="body">
    <div class="notification-container">
      <transition-group name="notification" tag="div">
        <v-alert
          v-for="notification in notifications"
          :key="notification.id"
          :type="notification.type"
          class="notification-item mb-3"
          variant="tonal"
          closable
          @click:close="remove(notification.id)"
        >
          {{ notification.message }}
        </v-alert>
      </transition-group>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { useNotification } from '@/composables'

const { notifications, remove } = useNotification()
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 80px;
  right: 24px;
  z-index: 9999;
  max-width: 400px;
  pointer-events: none;
}

.notification-item {
  pointer-events: all;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

/* Transition animations */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100px) scale(0.8);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100px) scale(0.8);
}

.notification-move {
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
