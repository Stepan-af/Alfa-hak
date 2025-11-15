/**
 * Search and Actions types for cross-module integration.
 */

export interface SearchResult {
  id: number
  type: 'task' | 'finance' | 'document' | 'marketing'
  title: string
  description: string
  created_at?: string
  relevance_score: number
  // Type-specific fields
  status?: string  // task
  priority?: string  // task
  amount?: number  // finance
  record_type?: string  // finance
  doc_type?: string  // document
  platform?: string  // marketing
}

export interface SearchResults {
  tasks: SearchResult[]
  finance: SearchResult[]
  documents: SearchResult[]
  marketing: SearchResult[]
  _meta?: {
    query: string
    total_results: number
    search_time: string
  }
}

export interface SuggestedAction {
  type: string
  title: string
  description: string
  parameters: Record<string, any>
  confidence: number
}

export interface ActionExecutionResult {
  success: boolean
  message: string
  data?: Record<string, any>
}

export interface RecentActivity {
  tasks: Array<{
    id: number
    type: 'task'
    title: string
    status: string
    created_at: string
  }>
  finance: Array<{
    id: number
    type: 'finance'
    title: string
    amount: number
    record_type: string
    date: string
  }>
  documents: Array<{
    id: number
    type: 'document'
    title: string
    doc_type: string
    created_at: string
  }>
  marketing: Array<{
    id: number
    type: 'marketing'
    title: string
    platform: string
    status: string
    created_at: string
  }>
}

export const ACTION_TYPES = {
  CREATE_TASK: 'create_task',
  ADD_EXPENSE: 'add_expense',
  ADD_INCOME: 'add_income',
  ANALYZE_FINANCE: 'analyze_finance',
  GENERATE_DOCUMENT: 'generate_document',
  CREATE_CAMPAIGN: 'create_campaign',
} as const

export const ACTION_ICONS: Record<string, string> = {
  create_task: 'mdi-checkbox-marked-circle-plus-outline',
  add_expense: 'mdi-cash-minus',
  add_income: 'mdi-cash-plus',
  analyze_finance: 'mdi-chart-line',
  generate_document: 'mdi-file-document-plus',
  create_campaign: 'mdi-bullhorn',
}

export const ACTION_COLORS: Record<string, string> = {
  create_task: 'primary',
  add_expense: 'error',
  add_income: 'success',
  analyze_finance: 'info',
  generate_document: 'warning',
  create_campaign: 'purple',
}

export const SEARCH_TYPE_LABELS: Record<string, string> = {
  tasks: 'Задачи',
  finance: 'Финансы',
  documents: 'Документы',
  marketing: 'Маркетинг',
}

export const SEARCH_TYPE_ICONS: Record<string, string> = {
  tasks: 'mdi-checkbox-marked-circle',
  finance: 'mdi-currency-rub',
  documents: 'mdi-file-document',
  marketing: 'mdi-bullhorn',
}
