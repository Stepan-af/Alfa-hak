import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// Direct imports instead of lazy loading
import HomeView from '@/views/HomeView.vue'
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
    component: HomeView
  },
  {
    path: '/finance',
    name: 'Finance',
    component: FinanceView
  },
  {
    path: '/documents',
    name: 'Documents',
    component: DocumentsView
  },
  {
    path: '/marketing',
    name: 'Marketing',
    component: MarketingView
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: TasksView
  },
  {
    path: '/chat',
    name: 'Chat',
    component: ChatView
  },
  {
    path: '/search',
    name: 'Search',
    component: SearchView
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
