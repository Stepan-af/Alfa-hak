<template>
  <v-menu
    v-model="searchMenu"
    :close-on-content-click="false"
    location="bottom"
    max-width="600"
  >
    <template #activator="{ props }">
      <v-text-field
        v-model="searchQuery"
        prepend-inner-icon="mdi-magnify"
        placeholder="Поиск по всем модулям..."
        density="compact"
        hide-details
        clearable
        variant="outlined"
        style="max-width: 400px"
        v-bind="props"
        @update:model-value="onSearchInput"
        @keydown.enter="performSearch"
        @click:clear="clearSearch"
      />
    </template>

    <v-card v-if="searchResults || isSearching" max-height="500" class="overflow-y-auto">
      <!-- Loading State -->
      <v-card-text v-if="isSearching" class="text-center py-8">
        <v-progress-circular indeterminate color="primary" />
        <div class="mt-2">Поиск...</div>
      </v-card-text>

      <!-- Results -->
      <div v-else-if="searchResults">
        <!-- Meta Info -->
        <v-card-title v-if="searchResults._meta" class="d-flex align-center">
          <span>Найдено: {{ searchResults._meta.total_results }}</span>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" size="small" @click="searchMenu = false" />
        </v-card-title>

        <!-- No Results -->
        <v-card-text v-if="searchResults._meta?.total_results === 0" class="text-center py-8">
          <v-icon size="64" color="grey">mdi-file-search</v-icon>
          <div class="text-h6 mt-2">Ничего не найдено</div>
          <div class="text-caption">Попробуйте изменить запрос</div>
        </v-card-text>

        <!-- Results by Type -->
        <div v-else>
          <!-- Tasks -->
          <v-list v-if="searchResults.tasks?.length > 0" density="compact">
            <v-list-subheader>
              <v-icon size="small" class="mr-2">{{ SEARCH_TYPE_ICONS.tasks }}</v-icon>
              {{ SEARCH_TYPE_LABELS.tasks }} ({{ searchResults.tasks.length }})
            </v-list-subheader>
            <v-list-item
              v-for="item in searchResults.tasks.slice(0, 5)"
              :key="`task-${item.id}`"
              @click="navigateToItem(item)"
            >
              <v-list-item-title>{{ item.title }}</v-list-item-title>
              <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
              <template #append>
                <v-chip size="x-small" :color="getPriorityColor(item.priority)">
                  {{ item.status }}
                </v-chip>
              </template>
            </v-list-item>
          </v-list>

          <v-divider v-if="searchResults.finance?.length > 0" />

          <!-- Finance -->
          <v-list v-if="searchResults.finance?.length > 0" density="compact">
            <v-list-subheader>
              <v-icon size="small" class="mr-2">{{ SEARCH_TYPE_ICONS.finance }}</v-icon>
              {{ SEARCH_TYPE_LABELS.finance }} ({{ searchResults.finance.length }})
            </v-list-subheader>
            <v-list-item
              v-for="item in searchResults.finance.slice(0, 5)"
              :key="`finance-${item.id}`"
              @click="navigateToItem(item)"
            >
              <v-list-item-title>{{ item.title }}</v-list-item-title>
              <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
              <template #append>
                <v-chip size="x-small" :color="item.record_type === 'income' ? 'success' : 'error'">
                  {{ item.amount }} ₽
                </v-chip>
              </template>
            </v-list-item>
          </v-list>

          <v-divider v-if="searchResults.documents?.length > 0" />

          <!-- Documents -->
          <v-list v-if="searchResults.documents?.length > 0" density="compact">
            <v-list-subheader>
              <v-icon size="small" class="mr-2">{{ SEARCH_TYPE_ICONS.documents }}</v-icon>
              {{ SEARCH_TYPE_LABELS.documents }} ({{ searchResults.documents.length }})
            </v-list-subheader>
            <v-list-item
              v-for="item in searchResults.documents.slice(0, 5)"
              :key="`doc-${item.id}`"
              @click="navigateToItem(item)"
            >
              <v-list-item-title>{{ item.title }}</v-list-item-title>
              <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>

          <v-divider v-if="searchResults.marketing?.length > 0" />

          <!-- Marketing -->
          <v-list v-if="searchResults.marketing?.length > 0" density="compact">
            <v-list-subheader>
              <v-icon size="small" class="mr-2">{{ SEARCH_TYPE_ICONS.marketing }}</v-icon>
              {{ SEARCH_TYPE_LABELS.marketing }} ({{ searchResults.marketing.length }})
            </v-list-subheader>
            <v-list-item
              v-for="item in searchResults.marketing.slice(0, 5)"
              :key="`marketing-${item.id}`"
              @click="navigateToItem(item)"
            >
              <v-list-item-title>{{ item.title }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ item.platform }} - {{ item.status }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </div>
      </div>
    </v-card>
  </v-menu>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { searchAll } from '@/api/integration'
import type { SearchResults, SearchResult } from '@/types/integration'
import { SEARCH_TYPE_LABELS, SEARCH_TYPE_ICONS } from '@/types/integration'
import { useNotification } from '@/composables/useNotification'

const router = useRouter()
const { show: showNotification } = useNotification()

const searchQuery = ref('')
const searchMenu = ref(false)
const searchResults = ref<SearchResults | null>(null)
const isSearching = ref(false)
let searchTimeout: NodeJS.Timeout | null = null

const onSearchInput = (value: string) => {
  if (!value || value.length < 2) {
    searchResults.value = null
    return
  }

  // Debounce search
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  searchTimeout = setTimeout(() => {
    performSearch()
  }, 500)
}

const performSearch = async () => {
  if (!searchQuery.value || searchQuery.value.length < 2) return

  isSearching.value = true
  searchMenu.value = true

  try {
    searchResults.value = await searchAll(searchQuery.value)
  } catch (error: any) {
    showNotification('Ошибка поиска', 'error')
    searchResults.value = null
  } finally {
    isSearching.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = null
  searchMenu.value = false
}

const navigateToItem = (item: SearchResult) => {
  searchMenu.value = false
  
  const routes: Record<string, string> = {
    task: '/tasks',
    finance: '/finance',
    document: '/documents',
    marketing: '/marketing',
  }

  const route = routes[item.type]
  if (route) {
    router.push(route)
    // Optional: emit event to highlight specific item
    // eventBus.$emit('highlight-item', { type: item.type, id: item.id })
  }
}

const getPriorityColor = (priority?: string) => {
  const colors: Record<string, string> = {
    urgent: 'error',
    high: 'warning',
    medium: 'info',
    low: 'grey',
  }
  return colors[priority || 'medium'] || 'grey'
}
</script>

<style scoped>
.overflow-y-auto {
  overflow-y: auto;
}
</style>
