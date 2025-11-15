<template>
  <v-app>
    <!-- App Bar -->
    <v-app-bar
      elevation="0"
      color="surface"
      class="app-bar"
    >
      <v-app-bar-title class="d-flex align-center">
        <span class="alfa-logo">Alfa</span>
        <span class="ml-2">Copilot</span>
      </v-app-bar-title>

      <v-spacer></v-spacer>

      <!-- Global Search -->
      <GlobalSearch class="mr-4" />

      <!-- User Menu -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
          >
            <v-avatar color="primary" size="40">
              <span class="text-white">{{ userInitials }}</span>
            </v-avatar>
          </v-btn>
        </template>
        <v-list>
          <v-list-item>
            <v-list-item-title>MVP User</v-list-item-title>
            <v-list-item-subtitle>mvp@local</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Navigation Drawer -->
    <v-navigation-drawer
      v-model="drawer"
      color="surface"
      class="navigation-drawer"
    >
      <v-list nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          :prepend-icon="item.icon"
          :title="item.title"
          :active="isActive(item.path)"
        ></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- Main Content -->
    <v-main>
      <router-view></router-view>
    </v-main>

    <!-- Notification Container -->
    <NotificationContainer />
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import NotificationContainer from '@/components/NotificationContainer.vue'
import GlobalSearch from '@/components/GlobalSearch.vue'

const route = useRoute()

const drawer = ref(true)

const menuItems = [
  { path: '/', icon: 'mdi-home', title: 'Главная' },
  { path: '/finance', icon: 'mdi-chart-line', title: 'Финансы' },
  { path: '/documents', icon: 'mdi-file-document', title: 'Документы' },
  { path: '/marketing', icon: 'mdi-bullhorn', title: 'Маркетинг' },
  { path: '/tasks', icon: 'mdi-clipboard-check', title: 'Задачи' },
  { path: '/chat', icon: 'mdi-message', title: 'Чат' },
]

const userInitials = computed(() => {
  return 'MU' // MVP User
})

const isActive = (path: string) => {
  return route.path === path
}
</script>

<style scoped>
.alfa-logo {
  color: var(--v-theme-primary);
  font-weight: 700;
  font-size: 1.25rem;
}

.app-bar {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.navigation-drawer {
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

/* Page transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<style>
#app {
  min-height: 100vh;
}
</style>
