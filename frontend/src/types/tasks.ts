// === Base Task Types ===
export interface Task {
  id: number
  user_id: number
  title: string
  description?: string
  priority: string // "low" | "medium" | "high" | "urgent"
  status: string // "todo" | "in_progress" | "done" | "cancelled"
  due_date?: string // ISO datetime
  completed_at?: string // ISO datetime
  reminder_at?: string // ISO datetime
  category?: string
  tags?: string[]
  ai_suggested: boolean
  ai_context?: string
  is_recurring: boolean
  recurrence_pattern?: string // "daily" | "weekly" | "monthly"
  parent_task_id?: number
  attachments?: Array<{url: string; name: string; type: string}>
  linked_document_id?: number
  estimated_minutes?: number
  actual_minutes?: number
  created_at: string
  updated_at: string
  subtasks?: Task[]
}

export interface TaskCreate {
  title: string
  description?: string
  priority?: string
  status?: string
  due_date?: string
  reminder_at?: string
  category?: string
  tags?: string[]
  estimated_minutes?: number
}

export interface TaskUpdate {
  title?: string
  description?: string
  priority?: string
  status?: string
  due_date?: string
  completed_at?: string
  reminder_at?: string
  category?: string
  tags?: string[]
  estimated_minutes?: number
  actual_minutes?: number
}

// === AI Suggestions ===
export interface TaskSuggestionRequest {
  context: string
  count?: number
  priority?: string
  category?: string
}

export interface TaskSuggestion {
  title: string
  description: string
  priority: string
  category: string
  estimated_minutes?: number
  tags: string[]
}

export interface TaskSuggestionsResponse {
  suggestions: TaskSuggestion[]
}

// === Statistics ===
export interface TaskStatistics {
  total_tasks: number
  todo_tasks: number
  in_progress_tasks: number
  done_tasks: number
  cancelled_tasks: number
  overdue_tasks: number
  today_tasks: number
  this_week_tasks: number
  high_priority_tasks: number
  urgent_priority_tasks: number
  completion_rate: number
  average_completion_minutes?: number
  tasks_by_category: Record<string, number>
  tasks_by_priority: Record<string, number>
}

// === Productivity ===
export interface ProductivityInsight {
  type: string // "warning" | "tip" | "achievement"
  title: string
  message: string
  action?: string
}

export interface ProductivityReport {
  period: string // "today" | "this_week" | "this_month"
  completed_tasks: number
  total_time_minutes: number
  most_productive_category?: string
  insights: ProductivityInsight[]
}

// === Bulk Operations ===
export interface BulkUpdateTasksRequest {
  task_ids: number[]
  status?: string
  priority?: string
  category?: string
}

export interface BulkDeleteTasksRequest {
  task_ids: number[]
}

// === UI Helper Types ===
export interface PriorityOption {
  value: string
  label: string
  color: string
  icon: string
}

export interface StatusOption {
  value: string
  label: string
  color: string
  icon: string
}

export interface CategoryOption {
  value: string
  label: string
  icon: string
}

export const PRIORITIES: PriorityOption[] = [
  { value: 'low', label: 'Низкий', color: 'blue-grey', icon: 'mdi-flag-outline' },
  { value: 'medium', label: 'Средний', color: 'blue', icon: 'mdi-flag' },
  { value: 'high', label: 'Высокий', color: 'orange', icon: 'mdi-flag' },
  { value: 'urgent', label: 'Срочно', color: 'red', icon: 'mdi-flag' }
]

export const STATUSES: StatusOption[] = [
  { value: 'todo', label: 'К выполнению', color: 'grey', icon: 'mdi-circle-outline' },
  { value: 'in_progress', label: 'В работе', color: 'blue', icon: 'mdi-progress-clock' },
  { value: 'done', label: 'Выполнено', color: 'green', icon: 'mdi-check-circle' },
  { value: 'cancelled', label: 'Отменено', color: 'red-grey', icon: 'mdi-cancel' }
]

export const CATEGORIES: CategoryOption[] = [
  { value: 'finance', label: 'Финансы', icon: 'mdi-currency-usd' },
  { value: 'marketing', label: 'Маркетинг', icon: 'mdi-bullhorn' },
  { value: 'documents', label: 'Документы', icon: 'mdi-file-document' },
  { value: 'meetings', label: 'Встречи', icon: 'mdi-calendar-account' },
  { value: 'research', label: 'Исследования', icon: 'mdi-magnify' },
  { value: 'development', label: 'Разработка', icon: 'mdi-code-tags' },
  { value: 'sales', label: 'Продажи', icon: 'mdi-cart' },
  { value: 'support', label: 'Поддержка', icon: 'mdi-lifebuoy' },
  { value: 'other', label: 'Другое', icon: 'mdi-dots-horizontal' }
]

export const RECURRENCE_PATTERNS = [
  { value: 'daily', label: 'Ежедневно' },
  { value: 'weekly', label: 'Еженедельно' },
  { value: 'monthly', label: 'Ежемесячно' }
]

export const PRIORITY_COLORS: Record<string, string> = {
  low: 'blue-grey',
  medium: 'blue',
  high: 'orange',
  urgent: 'red'
}

export const STATUS_COLORS: Record<string, string> = {
  todo: 'grey',
  in_progress: 'blue',
  done: 'green',
  cancelled: 'red-grey'
}

export const PRIORITY_LABELS: Record<string, string> = {
  low: 'Низкий',
  medium: 'Средний',
  high: 'Высокий',
  urgent: 'Срочно'
}

export const STATUS_LABELS: Record<string, string> = {
  todo: 'К выполнению',
  in_progress: 'В работе',
  done: 'Выполнено',
  cancelled: 'Отменено'
}

// === Kanban Board Types ===
export interface KanbanColumn {
  status: string
  label: string
  tasks: Task[]
  color: string
}
