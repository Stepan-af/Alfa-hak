import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as tasksApi from '@/api/tasks'
import type {
  Task,
  TaskCreate,
  TaskUpdate,
  TaskSuggestionRequest,
  TaskSuggestionsResponse,
  TaskStatistics,
  ProductivityReport,
  KanbanColumn
} from '@/types/tasks'

export const useTasksStore = defineStore('tasks', () => {
  // State
  const tasks = ref<Task[]>([])
  const currentTask = ref<Task | null>(null)
  const statistics = ref<TaskStatistics | null>(null)
  const productivityReport = ref<ProductivityReport | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const todoTasks = computed(() =>
    tasks.value.filter((t) => t.status === 'todo')
  )

  const inProgressTasks = computed(() =>
    tasks.value.filter((t) => t.status === 'in_progress')
  )

  const doneTasks = computed(() =>
    tasks.value.filter((t) => t.status === 'done')
  )

  const overdueTasks = computed(() => {
    const now = new Date()
    return tasks.value.filter(
      (t) => t.due_date && new Date(t.due_date) < now && t.status !== 'done' && t.status !== 'cancelled'
    )
  })

  const todayTasks = computed(() => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)

    return tasks.value.filter((t) => {
      if (!t.due_date) return false
      const dueDate = new Date(t.due_date)
      return dueDate >= today && dueDate < tomorrow
    })
  })

  const urgentTasks = computed(() =>
    tasks.value.filter((t) => t.priority === 'urgent')
  )

  const highPriorityTasks = computed(() =>
    tasks.value.filter((t) => t.priority === 'high')
  )

  const tasksByCategory = computed(() => {
    const grouped: Record<string, Task[]> = {}
    tasks.value.forEach((t) => {
      if (t.category) {
        if (!grouped[t.category]) {
          grouped[t.category] = []
        }
        grouped[t.category].push(t)
      }
    })
    return grouped
  })

  const kanbanColumns = computed<KanbanColumn[]>(() => [
    {
      status: 'todo',
      label: 'К выполнению',
      tasks: todoTasks.value,
      color: 'grey'
    },
    {
      status: 'in_progress',
      label: 'В работе',
      tasks: inProgressTasks.value,
      color: 'blue'
    },
    {
      status: 'done',
      label: 'Выполнено',
      tasks: doneTasks.value,
      color: 'green'
    }
  ])

  // Actions
  const fetchTasks = async (filters?: {
    status?: string
    priority?: string
    category?: string
    is_overdue?: boolean
    search?: string
    skip?: number
    limit?: number
  }) => {
    isLoading.value = true
    error.value = null
    try {
      tasks.value = await tasksApi.getTasks(filters)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch tasks'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const fetchTask = async (taskId: number) => {
    isLoading.value = true
    error.value = null
    try {
      currentTask.value = await tasksApi.getTask(taskId)
      return currentTask.value
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch task'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const createTask = async (data: TaskCreate) => {
    isLoading.value = true
    error.value = null
    try {
      const task = await tasksApi.createTask(data)
      tasks.value.unshift(task)
      return task
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to create task'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const updateTask = async (taskId: number, data: TaskUpdate) => {
    isLoading.value = true
    error.value = null
    try {
      const task = await tasksApi.updateTask(taskId, data)
      const index = tasks.value.findIndex((t) => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = task
      }
      if (currentTask.value?.id === taskId) {
        currentTask.value = task
      }
      return task
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to update task'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const deleteTask = async (taskId: number) => {
    isLoading.value = true
    error.value = null
    try {
      await tasksApi.deleteTask(taskId)
      tasks.value = tasks.value.filter((t) => t.id !== taskId)
      if (currentTask.value?.id === taskId) {
        currentTask.value = null
      }
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to delete task'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const bulkUpdateTasks = async (taskIds: number[], updates: { status?: string; priority?: string; category?: string }) => {
    isLoading.value = true
    error.value = null
    try {
      const result = await tasksApi.bulkUpdateTasks({ task_ids: taskIds, ...updates })
      // Refresh tasks
      await fetchTasks()
      return result
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to bulk update tasks'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const bulkDeleteTasks = async (taskIds: number[]) => {
    isLoading.value = true
    error.value = null
    try {
      const result = await tasksApi.bulkDeleteTasks({ task_ids: taskIds })
      tasks.value = tasks.value.filter((t) => !taskIds.includes(t.id))
      return result
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to bulk delete tasks'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const getAISuggestions = async (request: TaskSuggestionRequest): Promise<TaskSuggestionsResponse> => {
    isLoading.value = true
    error.value = null
    try {
      return await tasksApi.getAISuggestions(request)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to get AI suggestions'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const fetchStatistics = async () => {
    isLoading.value = true
    error.value = null
    try {
      statistics.value = await tasksApi.getStatistics()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch statistics'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const fetchProductivityReport = async (period: string = 'this_week') => {
    isLoading.value = true
    error.value = null
    try {
      productivityReport.value = await tasksApi.getProductivityReport(period)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch productivity report'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const completeTask = async (taskId: number) => {
    isLoading.value = true
    error.value = null
    try {
      const task = await tasksApi.completeTask(taskId)
      const index = tasks.value.findIndex((t) => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = task
      }
      return task
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to complete task'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const startTask = async (taskId: number) => {
    isLoading.value = true
    error.value = null
    try {
      const task = await tasksApi.startTask(taskId)
      const index = tasks.value.findIndex((t) => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = task
      }
      return task
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to start task'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const cancelTask = async (taskId: number) => {
    isLoading.value = true
    error.value = null
    try {
      const task = await tasksApi.cancelTask(taskId)
      const index = tasks.value.findIndex((t) => t.id === taskId)
      if (index !== -1) {
        tasks.value[index] = task
      }
      return task
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to cancel task'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    tasks,
    currentTask,
    statistics,
    productivityReport,
    isLoading,
    error,
    // Computed
    todoTasks,
    inProgressTasks,
    doneTasks,
    overdueTasks,
    todayTasks,
    urgentTasks,
    highPriorityTasks,
    tasksByCategory,
    kanbanColumns,
    // Actions
    fetchTasks,
    fetchTask,
    createTask,
    updateTask,
    deleteTask,
    bulkUpdateTasks,
    bulkDeleteTasks,
    getAISuggestions,
    fetchStatistics,
    fetchProductivityReport,
    completeTask,
    startTask,
    cancelTask
  }
})
