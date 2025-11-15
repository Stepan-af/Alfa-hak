// ========== FinanceRecord Types ==========

export interface FinanceRecord {
  id: number
  user_id: number
  date: string
  description?: string
  amount: number
  category?: string
  subcategory?: string
  type: 'income' | 'expense'
  counterparty?: string
  payment_method?: string
  account?: string
  tags?: string[]
  notes?: string
  ai_category?: string
  ai_confidence?: number
  is_verified: boolean
  source_file?: string
  created_at: string
  updated_at?: string
}

export interface FinanceRecordCreate {
  date: string
  description?: string
  amount: number
  category?: string
  subcategory?: string
  type: 'income' | 'expense'
  counterparty?: string
  payment_method?: string
  account?: string
  tags?: string[]
  notes?: string
}

export interface FinanceRecordUpdate {
  date?: string
  description?: string
  amount?: number
  category?: string
  subcategory?: string
  type?: 'income' | 'expense'
  counterparty?: string
  payment_method?: string
  account?: string
  tags?: string[]
  notes?: string
  is_verified?: boolean
}

// ========== CSV Upload Types ==========

export interface CSVUploadResponse {
  success: boolean
  records_created: number
  records_failed: number
  errors: string[]
  file_name: string
}

// ========== Summary Types ==========

export interface CategorySummary {
  category: string
  amount: number
  count: number
  percentage: number
}

export interface FinanceSummary {
  total_income: number
  total_expense: number
  net_income: number
  transaction_count: number
  income_by_category: CategorySummary[]
  expense_by_category: CategorySummary[]
  period_start: string
  period_end: string
}

export interface TrendData {
  current_value: number
  previous_value: number
  change_percent: number
  change_absolute: number
  direction: 'up' | 'down' | 'neutral'
}

export interface FinanceSummaryWithTrends {
  total_income: TrendData
  total_expense: TrendData
  net_income: TrendData
  transaction_count: {
    current: number
    previous: number
    change: number
  }
  current_period: FinanceSummary
  previous_period: FinanceSummary
}

// ========== Cash Flow Types ==========

export interface MonthlyTrend {
  month: string
  income: number
  expense: number
  net: number
}

export interface CashFlowData {
  monthly_trends: MonthlyTrend[]
  average_income: number
  average_expense: number
  highest_income_month: string
  highest_expense_month: string
}

// ========== Budget Types ==========

export interface FinanceBudget {
  id: number
  user_id: number
  category: string
  amount: number
  period: 'monthly' | 'yearly'
  start_date: string
  end_date?: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface FinanceBudgetCreate {
  category: string
  amount: number
  period: 'monthly' | 'yearly'
  start_date: string
  end_date?: string
}

export interface FinanceBudgetUpdate {
  amount?: number
  period?: 'monthly' | 'yearly'
  end_date?: string
  is_active?: boolean
}

export interface BudgetStatus {
  budget: FinanceBudget
  spent: number
  remaining: number
  percentage_used: number
  is_over_budget: boolean
}

// ========== Goal Types ==========

export interface FinanceGoal {
  id: number
  user_id: number
  title: string
  description?: string
  target_amount: number
  current_amount: number
  deadline?: string
  status: 'active' | 'completed' | 'cancelled'
  progress_percentage: number
  created_at: string
  updated_at?: string
}

export interface FinanceGoalCreate {
  title: string
  description?: string
  target_amount: number
  deadline?: string
}

export interface FinanceGoalUpdate {
  title?: string
  description?: string
  target_amount?: number
  current_amount?: number
  deadline?: string
  status?: 'active' | 'completed' | 'cancelled'
}

// ========== Insights Types ==========

export interface AIInsight {
  type: 'warning' | 'tip' | 'opportunity'
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  category?: string
  amount?: number
}

export interface FinanceInsights {
  insights: AIInsight[]
  generated_at: string
}
