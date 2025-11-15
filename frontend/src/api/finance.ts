import apiClient from './client'
import type {
  FinanceRecord,
  FinanceRecordCreate,
  FinanceRecordUpdate,
  CSVUploadResponse,
  FinanceSummary,
  CashFlowData,
  FinanceInsights,
  FinanceBudget,
  FinanceBudgetCreate,
  FinanceBudgetUpdate,
  BudgetStatus,
  FinanceGoal,
  FinanceGoalCreate,
  FinanceGoalUpdate,
} from '@/types/finance'

export const financeAPI = {
  // ========== Транзакции ==========
  
  /**
   * Создать финансовую запись вручную
   */
  async createRecord(data: FinanceRecordCreate): Promise<FinanceRecord> {
    const response = await apiClient.post('/finance/records', data)
    return response.data
  },

  /**
   * Получить список финансовых записей
   */
  async getRecords(params?: {
    start_date?: string
    end_date?: string
    type?: 'income' | 'expense'
    category?: string
    limit?: number
    offset?: number
  }): Promise<FinanceRecord[]> {
    const response = await apiClient.get('/finance/records', { params })
    return response.data
  },

  /**
   * Получить одну финансовую запись
   */
  async getRecord(id: number): Promise<FinanceRecord> {
    const response = await apiClient.get(`/finance/records/${id}`)
    return response.data
  },

  /**
   * Обновить финансовую запись
   */
  async updateRecord(id: number, data: FinanceRecordUpdate): Promise<FinanceRecord> {
    const response = await apiClient.put(`/finance/records/${id}`, data)
    return response.data
  },

  /**
   * Удалить финансовую запись
   */
  async deleteRecord(id: number): Promise<void> {
    const response = await apiClient.delete(`/finance/records/${id}`)
    return response.data
  },

  // ========== CSV Upload ==========
  
  /**
   * Загрузить финансовые данные из CSV файла
   */
  async uploadCSV(file: File): Promise<CSVUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post('/finance/upload-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // ========== Аналитика ==========
  
  /**
   * Получить финансовую сводку за период
   */
  async getSummary(params?: {
    start_date?: string
    end_date?: string
  }): Promise<FinanceSummary> {
    const response = await apiClient.get('/finance/summary', { params })
    return response.data
  },

  /**
   * Получить данные денежного потока по месяцам
   */
  async getCashFlow(months: number = 12): Promise<CashFlowData> {
    const response = await apiClient.get('/finance/cash-flow', {
      params: { months },
    })
    return response.data
  },

  /**
   * Получить AI-инсайты и рекомендации
   */
  async getInsights(): Promise<FinanceInsights> {
    const response = await apiClient.get('/finance/insights')
    return response.data
  },

  /**
   * Получить список категорий
   */
  async getCategories(type: 'income' | 'expense'): Promise<string[]> {
    const response = await apiClient.get('/finance/categories', {
      params: { type },
    })
    return response.data
  },

  // ========== Бюджеты ==========
  
  /**
   * Создать бюджет
   */
  async createBudget(data: FinanceBudgetCreate): Promise<FinanceBudget> {
    const response = await apiClient.post('/finance/budgets', data)
    return response.data
  },

  /**
   * Получить список бюджетов
   */
  async getBudgets(activeOnly: boolean = true): Promise<FinanceBudget[]> {
    const response = await apiClient.get('/finance/budgets', {
      params: { active_only: activeOnly },
    })
    return response.data
  },

  /**
   * Получить статус выполнения бюджета
   */
  async getBudgetStatus(id: number): Promise<BudgetStatus> {
    const response = await apiClient.get(`/finance/budgets/${id}/status`)
    return response.data
  },

  /**
   * Обновить бюджет
   */
  async updateBudget(id: number, data: FinanceBudgetUpdate): Promise<FinanceBudget> {
    const response = await apiClient.put(`/finance/budgets/${id}`, data)
    return response.data
  },

  // ========== Финансовые цели ==========
  
  /**
   * Создать финансовую цель
   */
  async createGoal(data: FinanceGoalCreate): Promise<FinanceGoal> {
    const response = await apiClient.post('/finance/goals', data)
    return response.data
  },

  /**
   * Получить список финансовых целей
   */
  async getGoals(status?: 'active' | 'completed' | 'cancelled'): Promise<FinanceGoal[]> {
    const response = await apiClient.get('/finance/goals', {
      params: status ? { status } : undefined,
    })
    return response.data
  },

  /**
   * Обновить финансовую цель
   */
  async updateGoal(id: number, data: FinanceGoalUpdate): Promise<FinanceGoal> {
    const response = await apiClient.put(`/finance/goals/${id}`, data)
    return response.data
  },
}
