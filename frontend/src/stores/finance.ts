import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { financeAPI } from '@/api/finance'
import type {
  FinanceRecord,
  FinanceRecordCreate,
  FinanceRecordUpdate,
  FinanceSummary,
  FinanceSummaryWithTrends,
  CashFlowData,
  FinanceInsights,
  FinanceBudget,
  FinanceBudgetCreate,
  BudgetStatus,
  FinanceGoal,
  FinanceGoalCreate,
} from '@/types/finance'

export const useFinanceStore = defineStore('finance', () => {
  // ========== State ==========
  const records = ref<FinanceRecord[]>([])
  const currentSummary = ref<FinanceSummary | null>(null)
  const summaryWithTrends = ref<FinanceSummaryWithTrends | null>(null)
  const cashFlowData = ref<CashFlowData | null>(null)
  const insights = ref<FinanceInsights | null>(null)
  const budgets = ref<FinanceBudget[]>([])
  const goals = ref<FinanceGoal[]>([])
  
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ========== Computed ==========
  const totalIncome = computed(() => currentSummary.value?.total_income || 0)
  const totalExpense = computed(() => currentSummary.value?.total_expense || 0)
  const netIncome = computed(() => currentSummary.value?.net_income || 0)
  
  const incomeRecords = computed(() => records.value.filter(r => r.type === 'income'))
  const expenseRecords = computed(() => records.value.filter(r => r.type === 'expense'))
  
  const activeBudgets = computed(() => budgets.value.filter(b => b.is_active))
  const activeGoals = computed(() => goals.value.filter(g => g.status === 'active'))
  
  // ========== Actions: Records ==========
  
  async function fetchRecords(params?: {
    start_date?: string
    end_date?: string
    type?: 'income' | 'expense'
    category?: string
  }) {
    try {
      loading.value = true
      error.value = null
      records.value = await financeAPI.getRecords(params)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки транзакций'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createRecord(data: FinanceRecordCreate) {
    try {
      loading.value = true
      error.value = null
      const newRecord = await financeAPI.createRecord(data)
      records.value.unshift(newRecord)
      // Обновляем сводку после добавления
      await fetchSummary()
      return newRecord
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка создания транзакции'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateRecord(id: number, data: FinanceRecordUpdate) {
    try {
      loading.value = true
      error.value = null
      const updated = await financeAPI.updateRecord(id, data)
      const index = records.value.findIndex(r => r.id === id)
      if (index !== -1) {
        records.value[index] = updated
      }
      await fetchSummary()
      return updated
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка обновления транзакции'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteRecord(id: number) {
    try {
      loading.value = true
      error.value = null
      await financeAPI.deleteRecord(id)
      records.value = records.value.filter(r => r.id !== id)
      await fetchSummary()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка удаления транзакции'
      throw e
    } finally {
      loading.value = false
    }
  }

  // ========== Actions: CSV Upload ==========
  
  async function uploadCSV(file: File) {
    try {
      loading.value = true
      error.value = null
      const response = await financeAPI.uploadCSV(file)
      // Перезагружаем данные после импорта
      await Promise.all([
        fetchRecords(),
        fetchSummary(),
      ])
      return response
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки CSV'
      throw e
    } finally {
      loading.value = false
    }
  }

  // ========== Actions: Analytics ==========
  
  async function fetchSummary(params?: {
    start_date?: string
    end_date?: string
  }) {
    try {
      loading.value = true
      error.value = null
      currentSummary.value = await financeAPI.getSummary(params)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки сводки'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchSummaryWithTrends() {
    try {
      loading.value = true
      error.value = null
      summaryWithTrends.value = await financeAPI.getSummaryWithTrends()
      // Также обновляем currentSummary для совместимости
      currentSummary.value = summaryWithTrends.value.current_period
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки сводки с трендами'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchCashFlow(months: number = 12) {
    try {
      loading.value = true
      error.value = null
      cashFlowData.value = await financeAPI.getCashFlow(months)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки графика'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchInsights() {
    try {
      loading.value = true
      error.value = null
      insights.value = await financeAPI.getInsights()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки инсайтов'
      throw e
    } finally {
      loading.value = false
    }
  }

  // ========== Actions: Budgets ==========
  
  async function fetchBudgets(activeOnly: boolean = true) {
    try {
      loading.value = true
      error.value = null
      budgets.value = await financeAPI.getBudgets(activeOnly)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки бюджетов'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createBudget(data: FinanceBudgetCreate) {
    try {
      loading.value = true
      error.value = null
      const newBudget = await financeAPI.createBudget(data)
      budgets.value.push(newBudget)
      return newBudget
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка создания бюджета'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function getBudgetStatus(id: number): Promise<BudgetStatus> {
    try {
      loading.value = true
      error.value = null
      return await financeAPI.getBudgetStatus(id)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки статуса бюджета'
      throw e
    } finally {
      loading.value = false
    }
  }

  // ========== Actions: Goals ==========
  
  async function fetchGoals(status?: 'active' | 'completed' | 'cancelled') {
    try {
      loading.value = true
      error.value = null
      goals.value = await financeAPI.getGoals(status)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки целей'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createGoal(data: FinanceGoalCreate) {
    try {
      loading.value = true
      error.value = null
      const newGoal = await financeAPI.createGoal(data)
      goals.value.push(newGoal)
      return newGoal
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка создания цели'
      throw e
    } finally {
      loading.value = false
    }
  }

  // ========== Utility ==========
  
  function clearError() {
    error.value = null
  }

  function $reset() {
    records.value = []
    currentSummary.value = null
    cashFlowData.value = null
    insights.value = null
    budgets.value = []
    goals.value = []
    loading.value = false
    error.value = null
  }

  return {
    // State
    records,
    currentSummary,
    summaryWithTrends,
    cashFlowData,
    insights,
    budgets,
    goals,
    loading,
    error,
    
    // Computed
    totalIncome,
    totalExpense,
    netIncome,
    incomeRecords,
    expenseRecords,
    activeBudgets,
    activeGoals,
    
    // Actions
    fetchRecords,
    createRecord,
    updateRecord,
    deleteRecord,
    uploadCSV,
    fetchSummary,
    fetchSummaryWithTrends,
    fetchCashFlow,
    fetchInsights,
    fetchBudgets,
    createBudget,
    getBudgetStatus,
    fetchGoals,
    createGoal,
    clearError,
    $reset,
  }
})
