import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Direct imports instead of lazy loading
import HomeView from '@/views/HomeView.vue'
import AuthView from '@/views/AuthView.vue'
import FinanceView from '@/views/FinanceView.vue'
import DocumentsView from '@/views/DocumentsView.vue'
import MarketingView from '@/views/MarketingView.vue'
import TasksView from '@/views/TasksView.vue'
import ChatView from '@/views/ChatView.vue'
import SearchView from '@/views/SearchView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/auth',
    name: 'Auth',
    component: AuthView,
    meta: { requiresAuth: false }
  },
  {
    path: '/auth/verify',
    name: 'AuthVerify',
    component: AuthView,
    meta: { requiresAuth: false }
  },
  {
    path: '/finance',
    name: 'Finance',
    component: FinanceView,
    meta: { requiresAuth: true }
  },
  {
    path: '/documents',
    name: 'Documents',
    component: DocumentsView,
    meta: { requiresAuth: true }
  },
  {
    path: '/marketing',
    name: 'Marketing',
    component: MarketingView,
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: TasksView,
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: ChatView,
    meta: { requiresAuth: true }
  },
  {
    path: '/search',
    name: 'Search',
    component: SearchView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation guard
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  // Check if route requires authentication
  if (requiresAuth) {
    // Try to restore auth from localStorage
    if (!authStore.isAuthenticated) {
      const isAuthenticated = await authStore.checkAuth()
      
      if (!isAuthenticated) {
        // Redirect to auth page
        next({
          name: 'Auth',
          query: { redirect: to.fullPath }
        })
        return
      }
    }
  }

  // If already authenticated and trying to access auth page, redirect to home
  if (to.name === 'Auth' && authStore.isAuthenticated) {
    next({ name: 'Home' })
    return
  }

  next()
})

export default router

