<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">🔍 Поиск</h1>

        <!-- Search Input -->
        <v-text-field
          v-model="searchQuery"
          prepend-inner-icon="mdi-magnify"
          placeholder="Поиск по всем модулям..."
          density="comfortable"
          variant="outlined"
          clearable
          autofocus
          @update:model-value="onSearchInput"
          @keydown.enter="performSearch"
        />

        <!-- Filters -->
        <v-chip-group
          v-model="selectedType"
          mandatory
          class="mb-4"
        >
          <v-chip value="all" size="small">Все</v-chip>
          <v-chip value="tasks" size="small">Задачи</v-chip>
          <v-chip value="finance" size="small">Финансы</v-chip>
          <v-chip value="documents" size="small">Документы</v-chip>
          <v-chip value="marketing" size="small">Маркетинг</v-chip>
        </v-chip-group>

        <!-- Loading -->
        <v-progress-linear v-if="isSearching" indeterminate color="primary" class="mb-4" />

        <!-- No Results -->
        <v-card v-if="!isSearching && searchResults && totalResults === 0" class="text-center pa-8">
          <v-icon size="64" color="grey">mdi-file-search</v-icon>
          <div class="text-h6 mt-4">Ничего не найдено</div>
          <div class="text-caption">Попробуйте изменить запрос или фильтры</div>
        </v-card>

        <!-- Results -->
        <div v-if="!isSearching && searchResults && totalResults > 0">
          <!-- Summary -->
          <div class="text-subtitle-1 mb-4">
            Найдено: <strong>{{ totalResults }}</strong> результатов
          </div>

          <!-- Tasks -->
          <v-card v-if="searchResults.tasks.length > 0" class="mb-4">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-checkbox-marked-circle</v-icon>
              Задачи ({{ searchResults.tasks.length }})
            </v-card-title>
            <v-divider />
            <v-list>
              <v-list-item
                v-for="task in searchResults.tasks"
                :key="`task-${task.id}`"
                :to="`/tasks`"
              >
                <template #prepend>
                  <v-chip :color="getPriorityColor(task.priority)" size="small">
                    {{ task.priority }}
                  </v-chip>
                </template>
                <v-list-item-title>{{ task.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ task.description }}</v-list-item-subtitle>
                <template #append>
                  <v-chip size="small" variant="outlined">{{ task.status }}</v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card>

          <!-- Finance -->
          <v-card v-if="searchResults.finance.length > 0" class="mb-4">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-currency-rub</v-icon>
              Финансы ({{ searchResults.finance.length }})
            </v-card-title>
            <v-divider />
            <v-list>
              <v-list-item
                v-for="record in searchResults.finance"
                :key="`finance-${record.id}`"
                :to="`/finance`"
              >
                <template #prepend>
                  <v-chip :color="record.record_type === 'income' ? 'success' : 'error'" size="small">
                    {{ record.record_type === 'income' ? '+' : '-' }}{{ record.amount }}₽
                  </v-chip>
                </template>
                <v-list-item-title>{{ record.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ record.description }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card>

          <!-- Documents -->
          <v-card v-if="searchResults.documents.length > 0" class="mb-4">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-file-document</v-icon>
              Документы ({{ searchResults.documents.length }})
            </v-card-title>
            <v-divider />
            <v-list>
              <v-list-item
                v-for="doc in searchResults.documents"
                :key="`doc-${doc.id}`"
                :to="`/documents`"
              >
                <template #prepend>
                  <v-icon>mdi-file</v-icon>
                </template>
                <v-list-item-title>{{ doc.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ doc.description }}</v-list-item-subtitle>
                <template #append>
                  <v-chip size="small" variant="outlined">{{ doc.doc_type }}</v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card>

          <!-- Marketing -->
          <v-card v-if="searchResults.marketing.length > 0" class="mb-4">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2">mdi-bullhorn</v-icon>
              Маркетинг ({{ searchResults.marketing.length }})
            </v-card-title>
            <v-divider />
            <v-list>
              <v-list-item
                v-for="campaign in searchResults.marketing"
                :key="`marketing-${campaign.id}`"
                :to="`/marketing`"
              >
                <template #prepend>
                  <v-chip size="small">{{ campaign.platform }}</v-chip>
                </template>
                <v-list-item-title>{{ campaign.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ campaign.description }}</v-list-item-subtitle>
                <template #append>
                  <v-chip size="small" variant="outlined">{{ campaign.status }}</v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { searchAll, searchByType } from '@/api/integration'
import type { SearchResults } from '@/types/integration'
import { useNotification } from '@/composables/useNotification'

const route = useRoute()
const { show: showNotification } = useNotification()

const searchQuery = ref('')
const selectedType = ref('all')
const searchResults = ref<SearchResults | null>(null)
const isSearching = ref(false)
let searchTimeout: ReturnType<typeof setTimeout> | null = null

const totalResults = computed(() => {
  if (!searchResults.value) return 0
  return (
    searchResults.value.tasks.length +
    searchResults.value.finance.length +
    searchResults.value.documents.length +
    searchResults.value.marketing.length
  )
})

const onSearchInput = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  if (searchQuery.value.length < 2) {
    searchResults.value = null
    return
  }

  searchTimeout = setTimeout(() => {
    performSearch()
  }, 500)
}

const performSearch = async () => {
  if (searchQuery.value.length < 2) return

  isSearching.value = true

  try {
    if (selectedType.value === 'all') {
      searchResults.value = await searchAll(searchQuery.value, 200)
    } else {
      const response = await searchByType(selectedType.value, searchQuery.value, 200)
      // Convert single-type results to SearchResults format
      const results = response.results || []
      searchResults.value = {
        tasks: selectedType.value === 'tasks' ? results : [],
        finance: selectedType.value === 'finance' ? results : [],
        documents: selectedType.value === 'documents' ? results : [],
        marketing: selectedType.value === 'marketing' ? results : [],
        _meta: {
          query: searchQuery.value,
          total_results: results.length,
          search_time: new Date().toISOString()
        }
      }
    }
  } catch (error: any) {
    showNotification('Ошибка поиска', 'error')
    searchResults.value = null
  } finally {
    isSearching.value = false
  }
}

const getPriorityColor = (priority?: string) => {
  const colors: Record<string, string> = {
    urgent: 'error',
    high: 'warning',
    medium: 'info',
    low: 'success',
  }
  return colors[priority || 'medium'] || 'grey'
}

// Watch for type changes
watch(selectedType, () => {
  if (searchQuery.value.length >= 2) {
    performSearch()
  }
})

// Initialize from query params
onMounted(() => {
  if (route.query.q) {
    searchQuery.value = route.query.q as string
    performSearch()
  }
  if (route.query.type) {
    selectedType.value = route.query.type as string
  }
})
</script>

<style scoped>
.v-list-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}
</style>