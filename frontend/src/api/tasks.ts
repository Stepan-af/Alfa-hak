import apiClient from './client'
import type {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskSuggestionRequest,
  TaskSuggestionsResponse,
  TaskStatistics,
  ProductivityReport,
  BulkUpdateTasksRequest,
  BulkDeleteTasksRequest
} from '@/types/tasks'

// === Task CRUD ===

export const createTask = async (data: TaskCreate): Promise<Task> => {
  const response = await apiClient.post('/tasks/tasks', data)
  return response.data
}

export const getTasks = async (params?: {
  status?: string
  priority?: string
  category?: string
  is_overdue?: boolean
  search?: string
  skip?: number
  limit?: number
}): Promise<Task[]> => {
  const response = await apiClient.get('/tasks/tasks', { params })
  return response.data
}

export const getTask = async (taskId: number): Promise<Task> => {
  const response = await apiClient.get(`/tasks/tasks/${taskId}`)
  return response.data
}

export const updateTask = async (taskId: number, data: TaskUpdate): Promise<Task> => {
  const response = await apiClient.put(`/tasks/tasks/${taskId}`, data)
  return response.data
}

export const deleteTask = async (taskId: number): Promise<void> => {
  await apiClient.delete(`/tasks/tasks/${taskId}`)
}

// === Bulk Operations ===

export const bulkUpdateTasks = async (data: BulkUpdateTasksRequest): Promise<{ updated: number }> => {
  const response = await apiClient.post(`/tasks/tasks/bulk-update`, data)
  return response.data
}

export const bulkDeleteTasks = async (data: BulkDeleteTasksRequest): Promise<{ deleted: number }> => {
  const response = await apiClient.post(`/tasks/tasks/bulk-delete`, data)
  return response.data
}

// === AI Suggestions ===

export const getAISuggestions = async (data: TaskSuggestionRequest): Promise<TaskSuggestionsResponse> => {
  const response = await apiClient.post(`/tasks/ai-suggestions`, data)
  return response.data
}

// === Statistics & Analytics ===

export const getStatistics = async (): Promise<TaskStatistics> => {
  const response = await apiClient.get(`/tasks/statistics`)
  return response.data
}

export const getProductivityReport = async (period: string = 'this_week'): Promise<ProductivityReport> => {
  const response = await apiClient.get(`/tasks/productivity-report`, {
    params: { period }
  })
  return response.data
}

// === Quick Actions ===

export const completeTask = async (taskId: number): Promise<Task> => {
  const response = await apiClient.post(`/tasks/tasks/${taskId}/complete`)
  return response.data
}

export const startTask = async (taskId: number): Promise<Task> => {
  const response = await apiClient.post(`/tasks/tasks/${taskId}/start`)
  return response.data
}

export const cancelTask = async (taskId: number): Promise<Task> => {
  const response = await apiClient.post(`/tasks/tasks/${taskId}/cancel`)
  return response.data
}
