<template>
  <v-container fluid>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h3 mb-2">✅ Задачи</h1>
        <p class="text-body-1">Управляйте задачами с AI-помощником</p>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row v-if="statistics">
      <v-col cols="12" sm="6" md="3">
        <StatWidget
          label="Всего задач"
          :value="statistics.total_tasks"
          icon="mdi-format-list-checks"
          icon-color="primary"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <StatWidget
          label="Выполнено"
          :value="`${statistics.completion_rate}%`"
          icon="mdi-check-circle"
          icon-color="success"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <StatWidget
          label="Просрочено"
          :value="statistics.overdue_tasks"
          icon="mdi-alert-circle"
          icon-color="error"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <StatWidget
          label="Сегодня"
          :value="statistics.today_tasks"
          icon="mdi-calendar-today"
          icon-color="info"
        />
      </v-col>
    </v-row>

    <!-- Action Buttons -->
    <v-row class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <ActionButton
          label="Добавить задачу"
          icon="mdi-plus"
          color="primary"
          size="large"
          block
          @click="openCreateDialog"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <ActionButton
          label="AI-предложения"
          icon="mdi-robot"
          color="success"
          size="large"
          block
          @click="openAISuggestionsDialog"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <ActionButton
          label="Продуктивность"
          icon="mdi-chart-line"
          color="warning"
          size="large"
          block
          @click="openProductivityDialog"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-btn-toggle v-model="viewMode" mandatory color="primary" density="comfortable">
          <v-tooltip text="Канбан доска" location="top" open-delay="300">
            <template #activator="{ props }">
              <v-btn value="kanban" icon="mdi-view-column" v-bind="props" />
            </template>
          </v-tooltip>
          <v-tooltip text="Список" location="top" open-delay="300">
            <template #activator="{ props }">
              <v-btn value="list" icon="mdi-view-list" v-bind="props" />
            </template>
          </v-tooltip>
        </v-btn-toggle>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-row class="mb-2">
      <v-col cols="12" md="3">
        <v-select
          v-model="priorityFilter"
          :items="PRIORITIES"
          item-title="label"
          item-value="value"
          label="Приоритет"
          clearable
          density="comfortable"
          @update:model-value="applyFilters"
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-select
          v-model="categoryFilter"
          :items="CATEGORIES"
          item-title="label"
          item-value="value"
          label="Категория"
          clearable
          density="comfortable"
          @update:model-value="applyFilters"
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-checkbox
          v-model="showOverdueOnly"
          label="Только просроченные"
          density="comfortable"
          @update:model-value="applyFilters"
        />
      </v-col>
      <v-col cols="12" md="3">
        <v-text-field
          v-model="searchQuery"
          label="Поиск"
          prepend-inner-icon="mdi-magnify"
          clearable
          density="comfortable"
          @update:model-value="applyFilters"
        />
      </v-col>
    </v-row>

    <!-- Kanban Board -->
    <v-row v-if="viewMode === 'kanban'">
      <v-col
        v-for="column in kanbanColumns"
        :key="column.status"
        cols="12"
        md="4"
      >
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-chip :color="column.color" size="small" class="mr-2">
              {{ column.tasks.length }}
            </v-chip>
            {{ column.label }}
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-2" style="min-height: 400px">
            <v-list density="compact">
              <draggable
                v-model="column.tasks"
                group="tasks"
                @change="onTaskDrop($event, column.status)"
                item-key="id"
              >
                <template #item="{ element: task }">
                  <v-list-item
                    class="mb-2 pa-2 rounded"
                    style="border: 1px solid #e0e0e0; cursor: move"
                    @click="viewTask(task)"
                  >
                    <template #prepend>
                      <v-icon :color="PRIORITY_COLORS[task.priority]" size="small">
                        {{ getPriorityIcon(task.priority) }}
                      </v-icon>
                    </template>
                    <v-list-item-title>{{ task.title }}</v-list-item-title>
                    <v-list-item-subtitle v-if="task.due_date">
                      <v-icon size="x-small">mdi-calendar</v-icon>
                      {{ formatDate(task.due_date) }}
                    </v-list-item-subtitle>
                    <template #append>
                      <v-menu>
                        <template #activator="{ props }">
                          <v-btn
                            icon="mdi-dots-vertical"
                            variant="text"
                            size="small"
                            v-bind="props"
                            @click.stop
                          />
                        </template>
                        <v-list>
                          <v-list-item @click="editTask(task)">
                            <template #prepend>
                              <v-icon>mdi-pencil</v-icon>
                            </template>
                            <v-list-item-title>Редактировать</v-list-item-title>
                          </v-list-item>
                          <v-list-item v-if="task.status !== 'done'" @click="completeTaskAction(task.id)">
                            <template #prepend>
                              <v-icon>mdi-check</v-icon>
                            </template>
                            <v-list-item-title>Завершить задачу</v-list-item-title>
                          </v-list-item>
                          <v-list-item @click="confirmDelete(task.id)">
                            <template #prepend>
                              <v-icon color="error">mdi-delete</v-icon>
                            </template>
                            <v-list-item-title>Удалить</v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-menu>
                    </template>
                  </v-list-item>
                </template>
              </draggable>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- List View -->
    <v-row v-else>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <span class="text-h5">Список задач</span>
            <v-spacer />
            <v-btn icon="mdi-refresh" variant="text" @click="loadTasks" />
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="tasks"
              :loading="isLoading"
              item-value="id"
            >
              <template #item.priority="{ item }">
                <v-chip :color="PRIORITY_COLORS[item.priority]" size="small">
                  <v-icon start size="small">{{ getPriorityIcon(item.priority) }}</v-icon>
                  {{ PRIORITY_LABELS[item.priority] }}
                </v-chip>
              </template>

              <template #item.status="{ item }">
                <v-chip :color="STATUS_COLORS[item.status]" size="small">
                  {{ STATUS_LABELS[item.status] }}
                </v-chip>
              </template>

              <template #item.due_date="{ item }">
                <span v-if="item.due_date" :class="{ 'text-error': isOverdue(item) }">
                  {{ formatDate(item.due_date) }}
                </span>
                <span v-else>—</span>
              </template>

              <template #item.actions="{ item }">
                <v-tooltip text="Просмотр" location="top" open-delay="300">
                  <template #activator="{ props }">
                    <v-btn
                      icon="mdi-eye"
                      variant="text"
                      size="small"
                      v-bind="props"
                      @click="viewTask(item)"
                    />
                  </template>
                </v-tooltip>
                
                <v-tooltip text="Редактировать" location="top" open-delay="300">
                  <template #activator="{ props }">
                    <v-btn
                      icon="mdi-pencil"
                      variant="text"
                      size="small"
                      v-bind="props"
                      @click="editTask(item)"
                    />
                  </template>
                </v-tooltip>
                
                <v-tooltip v-if="item.status !== 'done'" text="Завершить задачу" location="top" open-delay="300">
                  <template #activator="{ props }">
                    <v-btn
                      icon="mdi-check"
                      variant="text"
                      size="small"
                      color="success"
                      v-bind="props"
                      @click="completeTaskAction(item.id)"
                    />
                  </template>
                </v-tooltip>
                
                <v-tooltip text="Удалить" location="top" open-delay="300">
                  <template #activator="{ props }">
                    <v-btn
                      icon="mdi-delete"
                      variant="text"
                      size="small"
                      color="error"
                      v-bind="props"
                      @click="confirmDelete(item.id)"
                    />
                  </template>
                </v-tooltip>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Create/Edit Task Dialog -->
    <v-dialog v-model="taskDialog" max-width="700px" persistent>
      <v-card>
        <v-card-title>
          {{ editingTask ? 'Редактировать задачу' : 'Создать задачу' }}
        </v-card-title>
        <v-card-text>
          <v-form ref="taskForm">
            <v-text-field
              v-model="taskFormData.title"
              label="Название *"
              :rules="[rules.required]"
              density="comfortable"
            />
            <v-textarea
              v-model="taskFormData.description"
              label="Описание"
              rows="3"
              density="comfortable"
            />
            <v-row>
              <v-col cols="6">
                <v-select
                  v-model="taskFormData.priority"
                  :items="PRIORITIES"
                  item-title="label"
                  item-value="value"
                  label="Приоритет"
                  density="comfortable"
                />
              </v-col>
              <v-col cols="6">
                <v-select
                  v-model="taskFormData.status"
                  :items="STATUSES"
                  item-title="label"
                  item-value="value"
                  label="Статус"
                  density="comfortable"
                />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="6">
                <v-select
                  v-model="taskFormData.category"
                  :items="CATEGORIES"
                  item-title="label"
                  item-value="value"
                  label="Категория"
                  density="comfortable"
                />
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="taskFormData.due_date"
                  label="Срок выполнения"
                  type="datetime-local"
                  density="comfortable"
                />
              </v-col>
            </v-row>
            <v-combobox
              v-model="taskFormData.tags"
              label="Теги"
              multiple
              chips
              clearable
              density="comfortable"
            />
            <v-text-field
              v-model.number="taskFormData.estimated_minutes"
              label="Оценка времени (минуты)"
              type="number"
              density="comfortable"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="closeTaskDialog">Отмена</v-btn>
          <v-btn color="primary" @click="saveTask">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- AI Suggestions Dialog -->
    <v-dialog v-model="aiSuggestionsDialog" max-width="600px">
      <v-card>
        <v-card-title>🤖 AI-предложения задач</v-card-title>
        <v-card-text>
          <v-form ref="aiForm">
            <v-textarea
              v-model="aiContext"
              label="Опишите контекст вашего бизнеса *"
              :rules="[rules.required]"
              rows="3"
              density="comfortable"
              placeholder="Например: Открываю кофейню, нужно подготовить документы и запустить рекламу"
            />
            <v-text-field
              v-model.number="aiCount"
              label="Количество предложений"
              type="number"
              min="1"
              max="10"
              density="comfortable"
            />
          </v-form>

          <!-- AI Suggestions List -->
          <v-list v-if="aiSuggestions.length" class="mt-4">
            <v-list-subheader>Предложенные задачи:</v-list-subheader>
            <v-list-item
              v-for="(suggestion, idx) in aiSuggestions"
              :key="idx"
              class="mb-2"
            >
              <template #prepend>
                <v-icon :color="PRIORITY_COLORS[suggestion.priority]">
                  {{ getPriorityIcon(suggestion.priority) }}
                </v-icon>
              </template>
              <v-list-item-title>{{ suggestion.title }}</v-list-item-title>
              <v-list-item-subtitle>{{ suggestion.description }}</v-list-item-subtitle>
              <template #append>
                <v-btn
                  icon="mdi-plus"
                  variant="text"
                  size="small"
                  @click="createTaskFromSuggestion(suggestion)"
                />
              </template>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="closeAISuggestionsDialog">Закрыть</v-btn>
          <v-btn color="primary" :loading="isLoading" @click="fetchAISuggestions">
            Получить предложения
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Productivity Dialog -->
    <v-dialog v-model="productivityDialog" max-width="600px">
      <v-card>
        <v-card-title>📊 Отчёт по продуктивности</v-card-title>
        <v-card-text>
          <v-select
            v-model="productivityPeriod"
            :items="[
              { value: 'today', label: 'Сегодня' },
              { value: 'this_week', label: 'Эта неделя' },
              { value: 'this_month', label: 'Этот месяц' }
            ]"
            item-title="label"
            item-value="value"
            label="Период"
            density="comfortable"
            @update:model-value="fetchProductivityReportData"
          />

          <v-card v-if="productivityReport" class="mt-4">
            <v-card-text>
              <v-row>
                <v-col cols="6">
                  <div class="text-h4">{{ productivityReport.completed_tasks }}</div>
                  <div class="text-caption">Выполнено задач</div>
                </v-col>
                <v-col cols="6">
                  <div class="text-h4">{{ Math.round(productivityReport.total_time_minutes / 60) }}ч</div>
                  <div class="text-caption">Затрачено времени</div>
                </v-col>
              </v-row>
              <v-divider class="my-4" />
              <div v-if="productivityReport.most_productive_category">
                <strong>Самая продуктивная категория:</strong>
                {{ productivityReport.most_productive_category }}
              </div>

              <!-- Insights -->
              <v-list v-if="productivityReport.insights.length" class="mt-4">
                <v-list-subheader>Инсайты:</v-list-subheader>
                <v-list-item
                  v-for="(insight, idx) in productivityReport.insights"
                  :key="idx"
                >
                  <template #prepend>
                    <v-icon :color="getInsightColor(insight.type)">
                      {{ getInsightIcon(insight.type) }}
                    </v-icon>
                  </template>
                  <v-list-item-title>{{ insight.title }}</v-list-item-title>
                  <v-list-item-subtitle>{{ insight.message }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="closeProductivityDialog">Закрыть</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTasksStore } from '@/stores/tasks'
import { storeToRefs } from 'pinia'
import { useNotification } from '@/composables/useNotification'
import StatWidget from '@/components/StatWidget.vue'
import ActionButton from '@/components/ActionButton.vue'
import draggable from 'vuedraggable'
import {
  PRIORITIES,
  STATUSES,
  CATEGORIES,
  PRIORITY_COLORS,
  STATUS_COLORS,
  PRIORITY_LABELS,
  STATUS_LABELS
} from '@/types/tasks'
import type { Task, TaskCreate, TaskSuggestion } from '@/types/tasks'

const tasksStore = useTasksStore()
const { tasks, statistics, kanbanColumns, productivityReport, isLoading } = storeToRefs(tasksStore)
const { show: showNotification } = useNotification()

// View mode
const viewMode = ref<'kanban' | 'list'>('kanban')

// Filters
const priorityFilter = ref<string>()
const categoryFilter = ref<string>()
const showOverdueOnly = ref(false)
const searchQuery = ref('')

// Table headers
const headers = [
  { title: 'ID', key: 'id', sortable: true },
  { title: 'Название', key: 'title', sortable: true },
  { title: 'Приоритет', key: 'priority', sortable: true },
  { title: 'Статус', key: 'status', sortable: true },
  { title: 'Категория', key: 'category', sortable: true },
  { title: 'Срок', key: 'due_date', sortable: true },
  { title: 'Действия', key: 'actions', sortable: false }
]

// Dialogs
const taskDialog = ref(false)
const aiSuggestionsDialog = ref(false)
const productivityDialog = ref(false)
const editingTask = ref<Task | null>(null)

// Forms
const taskFormData = ref<TaskCreate>({
  title: '',
  priority: 'medium',
  status: 'todo'
})

const aiContext = ref('')
const aiCount = ref(5)
const aiSuggestions = ref<TaskSuggestion[]>([])

const productivityPeriod = ref('this_week')

const rules = {
  required: (v: any) => !!v || 'Обязательное поле'
}

// Methods
const loadTasks = async () => {
  try {
    await tasksStore.fetchTasks({
      priority: priorityFilter.value,
      category: categoryFilter.value,
      is_overdue: showOverdueOnly.value || undefined,
      search: searchQuery.value || undefined
    })
    await tasksStore.fetchStatistics()
  } catch (error) {
    showNotification('Ошибка загрузки задач', 'error')
  }
}

const applyFilters = () => {
  loadTasks()
}

const openCreateDialog = () => {
  editingTask.value = null
  taskFormData.value = { title: '', priority: 'medium', status: 'todo' }
  taskDialog.value = true
}

const editTask = (task: Task) => {
  editingTask.value = task
  taskFormData.value = {
    title: task.title,
    description: task.description,
    priority: task.priority,
    status: task.status,
    due_date: task.due_date,
    category: task.category,
    tags: task.tags,
    estimated_minutes: task.estimated_minutes
  }
  taskDialog.value = true
}

const viewTask = (task: Task) => {
  // TODO: Implement task detail view
  showNotification(`Просмотр задачи: ${task.title}`, 'info')
}

const saveTask = async () => {
  try {
    if (editingTask.value) {
      await tasksStore.updateTask(editingTask.value.id, taskFormData.value)
      showNotification('Задача обновлена', 'success')
    } else {
      await tasksStore.createTask(taskFormData.value)
      showNotification('Задача создана', 'success')
    }
    closeTaskDialog()
  } catch (error) {
    showNotification('Ошибка сохранения', 'error')
  }
}

const closeTaskDialog = () => {
  taskDialog.value = false
  editingTask.value = null
}

const confirmDelete = async (id: number) => {
  if (confirm('Удалить задачу?')) {
    try {
      await tasksStore.deleteTask(id)
      showNotification('Задача удалена', 'success')
    } catch (error) {
      showNotification('Ошибка удаления', 'error')
    }
  }
}

const completeTaskAction = async (id: number) => {
  try {
    await tasksStore.completeTask(id)
    showNotification('Задача выполнена!', 'success')
  } catch (error) {
    showNotification('Ошибка', 'error')
  }
}

const onTaskDrop = async (event: any, newStatus: string) => {
  if (event.added) {
    const task = event.added.element
    try {
      await tasksStore.updateTask(task.id, { status: newStatus })
      showNotification('Статус обновлён', 'success')
    } catch (error) {
      showNotification('Ошибка обновления', 'error')
      await loadTasks() // Reload on error
    }
  }
}

const openAISuggestionsDialog = () => {
  aiContext.value = ''
  aiSuggestions.value = []
  aiSuggestionsDialog.value = true
}

const closeAISuggestionsDialog = () => {
  aiSuggestionsDialog.value = false
  aiSuggestions.value = []
}

const fetchAISuggestions = async () => {
  try {
    const response = await tasksStore.getAISuggestions({
      context: aiContext.value,
      count: aiCount.value
    })
    aiSuggestions.value = response.suggestions
    showNotification('Предложения получены!', 'success')
  } catch (error) {
    showNotification('Ошибка получения предложений', 'error')
  }
}

const createTaskFromSuggestion = (suggestion: TaskSuggestion) => {
  taskFormData.value = {
    title: suggestion.title,
    description: suggestion.description,
    priority: suggestion.priority,
    category: suggestion.category,
    tags: suggestion.tags,
    estimated_minutes: suggestion.estimated_minutes,
    status: 'todo'
  }
  closeAISuggestionsDialog()
  taskDialog.value = true
}

const openProductivityDialog = async () => {
  productivityDialog.value = true
  await fetchProductivityReportData()
}

const closeProductivityDialog = () => {
  productivityDialog.value = false
}

const fetchProductivityReportData = async () => {
  try {
    await tasksStore.fetchProductivityReport(productivityPeriod.value)
  } catch (error) {
    showNotification('Ошибка загрузки отчёта', 'error')
  }
}

const getPriorityIcon = (priority: string) => {
  return priority === 'urgent' || priority === 'high' ? 'mdi-flag' : 'mdi-flag-outline'
}

const getInsightIcon = (type: string) => {
  const icons: Record<string, string> = {
    warning: 'mdi-alert',
    tip: 'mdi-lightbulb',
    achievement: 'mdi-trophy'
  }
  return icons[type] || 'mdi-information'
}

const getInsightColor = (type: string) => {
  const colors: Record<string, string> = {
    warning: 'warning',
    tip: 'info',
    achievement: 'success'
  }
  return colors[type] || 'grey'
}

const isOverdue = (task: Task) => {
  if (!task.due_date || task.status === 'done' || task.status === 'cancelled') return false
  return new Date(task.due_date) < new Date()
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return 'Сегодня'
  if (days === 1) return 'Завтра'
  if (days === -1) return 'Вчера'
  if (days < -1) return `${Math.abs(days)} дн. назад`
  if (days > 0 && days <= 7) return `Через ${days} дн.`

  return date.toLocaleDateString('ru-RU', { month: 'short', day: 'numeric' })
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.text-error {
  color: rgb(var(--v-theme-error));
}
</style>
