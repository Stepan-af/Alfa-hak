<template>
  <div class="finance-view">
    <v-container>
      <!-- Header -->
      <div class="d-flex justify-space-between align-center mb-8">
        <div>
          <h1 class="text-h3 font-weight-bold mb-2">Финансы</h1>
          <p class="text-body-1 text-medium-emphasis">
            Управляйте доходами и расходами вашего бизнеса
          </p>
        </div>
        
        <div class="d-flex gap-3">
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="showAddRecordDialog = true"
          >
            Добавить транзакцию
          </v-btn>
          
          <v-btn
            color="success"
            prepend-icon="mdi-file-upload"
            @click="triggerFileUpload"
          >
            Загрузить CSV
          </v-btn>
          <input
            ref="fileInput"
            type="file"
            accept=".csv"
            style="display: none"
            @change="handleFileUpload"
          />
        </div>
      </div>

      <!-- Loading State -->
      <LoadingSpinner v-if="financeStore.loading" size="large" />

      <template v-else>
        <!-- Summary Cards -->
        <v-row class="mb-8">
          <v-col cols="12" md="3">
            <StatWidget
              :value="financeStore.totalIncome"
              label="Доходы"
              icon="mdi-trending-up"
              icon-color="success"
              format="currency"
            />
          </v-col>
          
          <v-col cols="12" md="3">
            <StatWidget
              :value="financeStore.totalExpense"
              label="Расходы"
              icon="mdi-trending-down"
              icon-color="error"
              format="currency"
            />
          </v-col>
          
          <v-col cols="12" md="3">
            <StatWidget
              :value="financeStore.netIncome"
              label="Чистая прибыль"
              icon="mdi-cash-multiple"
              :icon-color="financeStore.netIncome >= 0 ? 'success' : 'error'"
              format="currency"
            />
          </v-col>
          
          <v-col cols="12" md="3">
            <StatWidget
              :value="financeStore.currentSummary?.transaction_count || 0"
              label="Транзакций"
              icon="mdi-swap-horizontal"
              icon-color="info"
              format="number"
            />
          </v-col>
        </v-row>

        <!-- AI Insights -->
        <v-card v-if="financeStore.insights" class="mb-8" elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-lightbulb-on</v-icon>
            AI Инсайты и рекомендации
          </v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col
                v-for="(insight, index) in financeStore.insights.insights"
                :key="index"
                cols="12"
                md="4"
              >
                <v-alert
                  :type="getInsightType(insight.type)"
                  :icon="getInsightIcon(insight.type)"
                  variant="tonal"
                  class="h-100"
                >
                  <v-alert-title>{{ insight.title }}</v-alert-title>
                  {{ insight.description }}
                </v-alert>
              </v-col>
            </v-row>
            
            <v-alert v-if="financeStore.insights.insights.length === 0" type="info" variant="tonal">
              Пока нет рекомендаций. Добавьте больше транзакций для анализа.
            </v-alert>
          </v-card-text>
        </v-card>

        <!-- Recent Transactions -->
        <v-card elevation="2">
          <v-card-title>
            <div class="d-flex justify-space-between align-center w-100">
              <span>Недавние транзакции</span>
              
              <div class="d-flex gap-2">
                <v-chip-group v-model="typeFilter" mandatory>
                  <v-chip value="all" size="small">Все</v-chip>
                  <v-chip value="income" size="small" color="success">Доходы</v-chip>
                  <v-chip value="expense" size="small" color="error">Расходы</v-chip>
                </v-chip-group>
              </div>
            </div>
          </v-card-title>
          
          <v-card-text>
            <v-table v-if="filteredRecords.length > 0">
              <thead>
                <tr>
                  <th>Дата</th>
                  <th>Описание</th>
                  <th>Категория</th>
                  <th>Сумма</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="record in filteredRecords.slice(0, 10)"
                  :key="record.id"
                >
                  <td>{{ formatDate(record.date) }}</td>
                  <td>{{ record.description || '—' }}</td>
                  <td>
                    <v-chip size="small" :color="record.type === 'income' ? 'success' : 'error'" variant="tonal">
                      {{ record.category || 'Без категории' }}
                    </v-chip>
                  </td>
                  <td :class="record.type === 'income' ? 'text-success' : 'text-error'">
                    {{ record.type === 'income' ? '+' : '−' }}{{ formatCurrency(record.amount) }}
                  </td>
                  <td>
                    <v-btn
                      icon="mdi-pencil"
                      size="small"
                      variant="text"
                      @click="editRecord(record)"
                    ></v-btn>
                    <v-btn
                      icon="mdi-delete"
                      size="small"
                      variant="text"
                      color="error"
                      @click="deleteRecord(record.id)"
                    ></v-btn>
                  </td>
                </tr>
              </tbody>
            </v-table>
            
            <v-alert v-else type="info" variant="tonal" class="mt-4">
              Нет транзакций. Загрузите CSV или добавьте вручную.
            </v-alert>
          </v-card-text>
        </v-card>
      </template>
    </v-container>

    <!-- Add/Edit Record Dialog -->
    <v-dialog v-model="showAddRecordDialog" max-width="600px">
      <v-card>
        <v-card-title>
          {{ editingRecord ? 'Редактировать' : 'Добавить' }} транзакцию
        </v-card-title>
        
        <v-card-text>
          <v-form ref="recordForm">
            <v-row>
              <v-col cols="12">
                <v-btn-toggle v-model="recordData.type" mandatory color="primary" class="mb-4">
                  <v-btn value="income" prepend-icon="mdi-plus-circle">
                    Доход
                  </v-btn>
                  <v-btn value="expense" prepend-icon="mdi-minus-circle">
                    Расход
                  </v-btn>
                </v-btn-toggle>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="recordData.date"
                  label="Дата"
                  type="date"
                  :rules="[v => !!v || 'Обязательное поле']"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="recordData.amount"
                  label="Сумма"
                  type="number"
                  prefix="₽"
                  :rules="[v => !!v || 'Обязательное поле', v => v > 0 || 'Должно быть больше 0']"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="recordData.description"
                  label="Описание"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="recordData.category"
                  label="Категория"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="closeRecordDialog">Отмена</v-btn>
          <v-btn color="primary" @click="saveRecord">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFinanceStore } from '@/stores/finance'
import { useNotification } from '@/composables'
import { LoadingSpinner, StatWidget } from '@/components'
import type { FinanceRecord, FinanceRecordCreate } from '@/types/finance'

const financeStore = useFinanceStore()
const notification = useNotification()

// File upload
const fileInput = ref<HTMLInputElement>()

function triggerFileUpload() {
  fileInput.value?.click()
}

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  try {
    const result = await financeStore.uploadCSV(file)
    notification.success(
      `Загружено ${result.records_created} транзакций. Ошибок: ${result.records_failed}`
    )
  } catch (error) {
    notification.error('Ошибка загрузки CSV файла')
  } finally {
    // Reset input
    target.value = ''
  }
}

// Record management
const showAddRecordDialog = ref(false)
const editingRecord = ref<FinanceRecord | null>(null)
const recordForm = ref()

const recordData = ref<FinanceRecordCreate>({
  type: 'expense',
  date: new Date().toISOString().split('T')[0],
  amount: 0,
  description: '',
  category: '',
})

function editRecord(record: FinanceRecord) {
  editingRecord.value = record
  recordData.value = {
    type: record.type,
    date: record.date,
    amount: record.amount,
    description: record.description || '',
    category: record.category || '',
  }
  showAddRecordDialog.value = true
}

async function saveRecord() {
  const { valid } = await recordForm.value.validate()
  if (!valid) return
  
  try {
    if (editingRecord.value) {
      await financeStore.updateRecord(editingRecord.value.id, recordData.value)
      notification.success('Транзакция обновлена')
    } else {
      await financeStore.createRecord(recordData.value)
      notification.success('Транзакция добавлена')
    }
    closeRecordDialog()
  } catch (error) {
    notification.error('Ошибка сохранения транзакции')
  }
}

async function deleteRecord(id: number) {
  if (!confirm('Удалить транзакцию?')) return
  
  try {
    await financeStore.deleteRecord(id)
    notification.success('Транзакция удалена')
  } catch (error) {
    notification.error('Ошибка удаления транзакции')
  }
}

function closeRecordDialog() {
  showAddRecordDialog.value = false
  editingRecord.value = null
  recordData.value = {
    type: 'expense',
    date: new Date().toISOString().split('T')[0],
    amount: 0,
    description: '',
    category: '',
  }
}

// Filters
const typeFilter = ref('all')

const filteredRecords = computed(() => {
  if (typeFilter.value === 'all') return financeStore.records
  return financeStore.records.filter(r => r.type === typeFilter.value)
})

// Helpers
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

function getInsightType(type: string): 'error' | 'warning' | 'success' | 'info' {
  const map: Record<string, 'error' | 'warning' | 'success' | 'info'> = {
    warning: 'warning',
    tip: 'info',
    opportunity: 'success',
  }
  return map[type] || 'info'
}

function getInsightIcon(type: string): string {
  const map: Record<string, string> = {
    warning: 'mdi-alert',
    tip: 'mdi-lightbulb',
    opportunity: 'mdi-star',
  }
  return map[type] || 'mdi-information'
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    financeStore.fetchRecords(),
    financeStore.fetchSummary(),
    financeStore.fetchInsights(),
  ])
})
</script>

<style scoped>
.finance-view {
  padding: 24px 0;
  min-height: calc(100vh - 64px);
}
</style>
