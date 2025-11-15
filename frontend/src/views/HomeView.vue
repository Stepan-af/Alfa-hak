<template>
  <div ref="pageRef" class="home-view">
    <v-container>
      <!-- Welcome Section -->
      <div ref="welcomeSection" class="welcome-section mb-12">
        <h1 class="text-h2 font-weight-bold mb-2">
          Добро пожаловать! 👋
        </h1>
        <p class="text-h6 text-medium-emphasis">
          Чем я могу помочь вам сегодня?
        </p>
      </div>

      <!-- Quick Stats -->
      <div ref="statsContainer">
        <LoadingSpinner v-if="financeStore.loading" size="large" />
        <v-row v-else class="mb-12 stat-cards-row">
          <v-col
            v-for="(stat, index) in stats"
            :key="stat.label"
            cols="12"
            sm="6"
            md="3"
            class="stat-card-col"
          >
            <StatCard
              :value="stat.value"
              :label="stat.label"
              :icon="stat.icon"
              :icon-color="stat.color"
              :color="stat.cardColor"
              :trend="stat.trend"
              :trend-direction="stat.trendDirection"
              :delay="index * 0.1"
              animated
            />
          </v-col>
        </v-row>
      </div>

      <!-- Quick Actions -->
      <h2 class="text-h4 mb-6">Быстрые действия</h2>
      <div ref="featuresContainer">
        <v-row class="features-row">
          <v-col
            v-for="feature in features"
            :key="feature.name"
            cols="12"
            sm="6"
            md="4"
            class="feature-col"
          >
            <HeroCard
              :title="feature.name"
              :description="feature.description"
              :icon="feature.icon"
              :gradient-from="feature.gradientFrom"
              :gradient-to="feature.gradientTo"
              :to="feature.route"
              action="Открыть"
              :action-icon="feature.icon"
            />
          </v-col>
        </v-row>
      </div>

      <!-- Recent Activity Section -->
      <div ref="activitySection" class="mt-12">
        <h2 class="text-h4 mb-6">Недавняя активность</h2>
        <v-card elevation="1" class="activity-card">
          <v-card-text class="text-center pa-8">
            <v-icon size="64" color="grey-lighten-1" class="mb-4">
              mdi-chart-timeline-variant
            </v-icon>
            <p class="text-body-1 text-medium-emphasis">
              Здесь будет отображаться ваша недавняя активность
            </p>
          </v-card-text>
        </v-card>
      </div>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFinanceStore } from '@/stores/finance'
import { usePageTransition, useListEnterAnimation, useCardEnterAnimation } from '@/composables/useAnimations'
import { HeroCard, LoadingSpinner } from '@/components'
import StatCard from '@/components/StatCard.vue'

const financeStore = useFinanceStore()

// Refs for animated elements
const pageRef = ref<HTMLElement | null>(null)
const welcomeSection = ref<HTMLElement | null>(null)
const statsContainer = ref<HTMLElement | null>(null)
const featuresContainer = ref<HTMLElement | null>(null)
const activitySection = ref<HTMLElement | null>(null)

// Применяем анимации
usePageTransition(pageRef)

onMounted(async () => {
  // Загружаем данные с трендами
  await financeStore.fetchSummaryWithTrends()
  
  // Анимация приветствия
  useCardEnterAnimation(welcomeSection, 0.1)
  
  // Анимация карточек статистики с задержкой
  useListEnterAnimation(statsContainer, '.stat-card-col', 0.08)
  
  // Анимация карточек функций
  useListEnterAnimation(featuresContainer, '.feature-col', 0.1)
  
  // Анимация секции активности
  useCardEnterAnimation(activitySection, 0.3)
})

// Загружаем реальные данные с трендами
const stats = computed(() => {
  const trends = financeStore.summaryWithTrends
  
  if (!trends) {
    return [
      {
        value: financeStore.netIncome || 0,
        label: 'Чистая прибыль',
        icon: 'mdi-cash',
        color: 'success',
        cardColor: 'success' as const,
        trend: undefined,
        trendDirection: 'neutral' as const
      },
      {
        value: financeStore.currentSummary?.transaction_count || 0,
        label: 'Транзакций',
        icon: 'mdi-swap-horizontal',
        color: 'info',
        cardColor: 'info' as const,
        trend: undefined,
        trendDirection: 'neutral' as const
      },
      {
        value: financeStore.totalIncome || 0,
        label: 'Доходы',
        icon: 'mdi-trending-up',
        color: 'success',
        cardColor: 'success' as const,
        trend: undefined,
        trendDirection: 'neutral' as const
      },
      {
        value: financeStore.totalExpense || 0,
        label: 'Расходы',
        icon: 'mdi-trending-down',
        color: 'error',
        cardColor: 'warning' as const,
        trend: undefined,
        trendDirection: 'neutral' as const
      }
    ]
  }
  
  return [
    {
      value: trends.net_income.current_value,
      label: 'Чистая прибыль',
      icon: 'mdi-cash',
      color: trends.net_income.direction === 'up' ? 'success' : trends.net_income.direction === 'down' ? 'error' : 'info',
      cardColor: trends.net_income.direction === 'up' ? 'success' : trends.net_income.direction === 'down' ? 'error' : 'info',
      trend: trends.net_income.change_percent !== 0 ? `${trends.net_income.change_percent > 0 ? '+' : ''}${trends.net_income.change_percent}%` : undefined,
      trendDirection: trends.net_income.direction
    },
    {
      value: trends.transaction_count.current,
      label: 'Транзакций',
      icon: 'mdi-swap-horizontal',
      color: 'info',
      cardColor: 'info' as const,
      trend: trends.transaction_count.change !== 0 ? `${trends.transaction_count.change > 0 ? '+' : ''}${trends.transaction_count.change}` : undefined,
      trendDirection: trends.transaction_count.change > 0 ? 'up' : trends.transaction_count.change < 0 ? 'down' : 'neutral'
    },
    {
      value: trends.total_income.current_value,
      label: 'Доходы',
      icon: 'mdi-trending-up',
      color: 'success',
      cardColor: 'success' as const,
      trend: trends.total_income.change_percent !== 0 ? `${trends.total_income.change_percent > 0 ? '+' : ''}${trends.total_income.change_percent}%` : undefined,
      trendDirection: trends.total_income.direction
    },
    {
      value: trends.total_expense.current_value,
      label: 'Расходы',
      icon: 'mdi-trending-down',
      color: 'error',
      cardColor: 'warning' as const,
      trend: trends.total_expense.change_percent !== 0 ? `${trends.total_expense.change_percent > 0 ? '+' : ''}${trends.total_expense.change_percent}%` : undefined,
      trendDirection: trends.total_expense.direction
    }
  ]
})

const features = [
  {
    name: 'Финансы',
    description: 'Анализируйте доходы и расходы, планируйте бюджет и получайте прогнозы',
    route: '/finance',
    icon: 'mdi-chart-line',
    gradientFrom: '#22c55e',
    gradientTo: '#10b981'
  },
  {
    name: 'Документы',
    description: 'Создавайте договоры, акты и другие документы в несколько кликов',
    route: '/documents',
    icon: 'mdi-file-document',
    gradientFrom: '#3b82f6',
    gradientTo: '#2563eb'
  },
  {
    name: 'Маркетинг',
    description: 'Генерируйте контент для соцсетей и планируйте рекламные кампании',
    route: '/marketing',
    icon: 'mdi-bullhorn',
    gradientFrom: '#f59e0b',
    gradientTo: '#d97706'
  },
  {
    name: 'Задачи',
    description: 'Организуйте работу команды и отслеживайте выполнение задач',
    route: '/tasks',
    icon: 'mdi-clipboard-check',
    gradientFrom: '#ef3124',
    gradientTo: '#dc2626'
  },
  {
    name: 'Чат',
    description: 'Общайтесь с AI-помощником и получайте ответы на любые вопросы',
    route: '/chat',
    icon: 'mdi-message',
    gradientFrom: '#8b5cf6',
    gradientTo: '#7c3aed'
  }
]

onMounted(async () => {
  // Загружаем финансовые данные для статистики
  await Promise.all([
    financeStore.fetchRecords(),
    financeStore.fetchSummary()
  ])
})
</script>

<style scoped>
.home-view {
  padding: 40px 0;
  min-height: calc(100vh - 64px);
}

.welcome-section {
  padding: 40px 0;
  background: linear-gradient(135deg, rgba(239, 49, 36, 0.1) 0%, transparent 100%);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 48px;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-cards-row {
  perspective: 1000px;
}

.features-row {
  perspective: 1000px;
}

.activity-card {
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.activity-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

/* Responsive */
@media (prefers-reduced-motion: reduce) {
  .welcome-section {
    animation: none;
  }
  
  .activity-card:hover {
    transform: none;
  }
}
</style>
