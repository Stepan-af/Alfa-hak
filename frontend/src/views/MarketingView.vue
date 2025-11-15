<template>
  <v-container fluid>
    <v-row class="mb-4">
      <v-col cols="12">
        <h1 class="text-h3 mb-2">📢 Маркетинг</h1>
        <p class="text-body-1">Создавайте контент с помощью AI для социальных сетей</p>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <v-row v-if="statistics">
      <v-col cols="12" sm="6" md="3">
        <StatWidget
          label="Всего кампаний"
          :value="statistics.total_campaigns"
          icon="mdi-bullhorn"
          icon-color="primary"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <StatWidget
          label="Опубликовано"
          :value="statistics.published_campaigns"
          icon="mdi-check-circle"
          icon-color="success"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <StatWidget
          label="Запланировано"
          :value="statistics.scheduled_campaigns"
          icon="mdi-calendar-clock"
          icon-color="info"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <StatWidget
          label="Вовлечённость"
          :value="`${statistics.average_engagement_rate}%`"
          icon="mdi-heart"
          icon-color="error"
        />
      </v-col>
    </v-row>

    <!-- Action Buttons -->
    <v-row class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <ActionButton
          label="Создать кампанию"
          icon="mdi-plus"
          color="primary"
          size="large"
          block
          @click="openCreateDialog"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <ActionButton
          label="Генератор контента"
          icon="mdi-magic-staff"
          color="success"
          size="large"
          block
          @click="openGeneratorDialog"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <ActionButton
          label="Идеи для контента"
          icon="mdi-lightbulb"
          color="warning"
          size="large"
          block
          @click="openIdeasDialog"
        />
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <ActionButton
          label="Календарь контента"
          icon="mdi-calendar"
          color="info"
          size="large"
          block
          @click="showCalendar = true"
        />
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-row class="mb-2">
      <v-col cols="12" md="4">
        <v-select
          v-model="statusFilter"
          :items="statusOptions"
          label="Фильтр по статусу"
          clearable
          density="comfortable"
          @update:model-value="applyFilters"
        />
      </v-col>
      <v-col cols="12" md="4">
        <v-select
          v-model="platformFilter"
          :items="PLATFORMS"
          item-title="label"
          item-value="value"
          label="Фильтр по платформе"
          clearable
          density="comfortable"
          @update:model-value="applyFilters"
        />
      </v-col>
    </v-row>

    <!-- Campaigns Table -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <span class="text-h5">Кампании</span>
            <v-spacer />
            <v-btn icon="mdi-refresh" variant="text" @click="loadCampaigns" />
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="campaigns"
              :loading="isLoading"
              item-value="id"
            >
              <template #item.platform="{ item }">
                <v-chip :color="getPlatformColor(item.platform)" size="small">
                  <v-icon start>{{ getPlatformIcon(item.platform) }}</v-icon>
                  {{ item.platform }}
                </v-chip>
              </template>

              <template #item.status="{ item }">
                <v-chip :color="STATUS_COLORS[item.status]" size="small">
                  {{ STATUS_LABELS[item.status] }}
                </v-chip>
              </template>

              <template #item.ai_generated="{ item }">
                <v-icon v-if="item.ai_generated === 'true'" color="success">
                  mdi-robot
                </v-icon>
              </template>

              <template #item.scheduled_date="{ item }">
                {{ item.scheduled_date ? formatDate(item.scheduled_date) : '—' }}
              </template>

              <template #item.actions="{ item }">
                <v-tooltip text="Просмотр" location="top" open-delay="300">
                  <template #activator="{ props }">
                    <v-btn
                      icon="mdi-eye"
                      variant="text"
                      size="small"
                      v-bind="props"
                      @click="viewCampaign(item)"
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
                      @click="editCampaign(item)"
                    />
                  </template>
                </v-tooltip>
                
                <v-tooltip v-if="item.status === 'draft'" text="Опубликовать" location="top" open-delay="300">
                  <template #activator="{ props }">
                    <v-btn
                      icon="mdi-send"
                      variant="text"
                      size="small"
                      color="success"
                      v-bind="props"
                      @click="publishCampaignAction(item.id)"
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

    <!-- Create/Edit Campaign Dialog -->
    <v-dialog v-model="campaignDialog" max-width="800px" persistent>
      <v-card>
        <v-card-title>
          {{ editingCampaign ? 'Редактировать кампанию' : 'Создать кампанию' }}
        </v-card-title>
        <v-card-text>
          <v-form ref="campaignForm">
            <v-text-field
              v-model="campaignFormData.title"
              label="Название *"
              :rules="[rules.required]"
              density="comfortable"
            />
            <v-textarea
              v-model="campaignFormData.description"
              label="Описание"
              rows="2"
              density="comfortable"
            />
            <v-textarea
              v-model="campaignFormData.content"
              label="Контент"
              rows="5"
              density="comfortable"
            />
            <v-select
              v-model="campaignFormData.platform"
              :items="PLATFORMS"
              item-title="label"
              item-value="value"
              label="Платформа"
              density="comfortable"
            />
            <v-select
              v-model="campaignFormData.content_type"
              :items="CONTENT_TYPES"
              item-title="label"
              item-value="value"
              label="Тип контента"
              density="comfortable"
            />
            <v-text-field
              v-model="campaignFormData.target_audience"
              label="Целевая аудитория"
              density="comfortable"
            />
            <v-combobox
              v-model="campaignFormData.tags"
              label="Хештеги"
              multiple
              chips
              clearable
              density="comfortable"
            />
            <v-text-field
              v-model="campaignFormData.scheduled_date"
              label="Дата публикации"
              type="date"
              density="comfortable"
            />
            <v-select
              v-model="campaignFormData.status"
              :items="statusOptions"
              label="Статус"
              density="comfortable"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="closeCampaignDialog">Отмена</v-btn>
          <v-btn color="primary" @click="saveCampaign">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- AI Content Generator Dialog -->
    <v-dialog v-model="generatorDialog" max-width="700px" persistent>
      <v-card>
        <v-card-title>✨ Генератор контента</v-card-title>
        <v-card-text>
          <v-form ref="generatorForm">
            <v-text-field
              v-model="generatorData.title"
              label="Тема *"
              :rules="[rules.required]"
              density="comfortable"
            />
            <v-select
              v-model="generatorData.platform"
              :items="PLATFORMS"
              item-title="label"
              item-value="value"
              label="Платформа *"
              :rules="[rules.required]"
              density="comfortable"
            />
            <v-select
              v-model="generatorData.content_type"
              :items="CONTENT_TYPES"
              item-title="label"
              item-value="value"
              label="Тип контента *"
              :rules="[rules.required]"
              density="comfortable"
            />
            <v-text-field
              v-model="generatorData.target_audience"
              label="Целевая аудитория"
              density="comfortable"
            />
            <v-select
              v-model="generatorData.tone"
              :items="TONES"
              item-title="label"
              item-value="value"
              label="Тон"
              density="comfortable"
            />
            <v-combobox
              v-model="generatorData.keywords"
              label="Ключевые слова"
              multiple
              chips
              clearable
              density="comfortable"
            />
            <v-select
              v-model="generatorData.length"
              :items="['short', 'medium', 'long']"
              label="Длина"
              density="comfortable"
            />
            <v-checkbox
              v-model="generatorData.include_hashtags"
              label="Включить хештеги"
              density="comfortable"
            />
            <v-checkbox
              v-model="generatorData.include_emoji"
              label="Включить эмодзи"
              density="comfortable"
            />
            <v-textarea
              v-model="generatorData.additional_instructions"
              label="Дополнительные инструкции"
              rows="2"
              density="comfortable"
            />
          </v-form>

          <!-- Generated Content -->
          <v-alert v-if="generatedContent" type="success" class="mt-4">
            <div class="text-h6 mb-2">Сгенерированный контент:</div>
            <pre class="text-body-2">{{ generatedContent.content }}</pre>
            <div v-if="generatedContent.hashtags?.length" class="mt-2">
              <v-chip
                v-for="tag in generatedContent.hashtags"
                :key="tag"
                size="small"
                class="mr-1"
              >
                {{ tag }}
              </v-chip>
            </div>
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="closeGeneratorDialog">Отмена</v-btn>
          <v-btn
            v-if="generatedContent"
            color="success"
            @click="createCampaignFromGenerated"
          >
            Создать кампанию
          </v-btn>
          <v-btn color="primary" :loading="isLoading" @click="generateContentAction">
            Генерировать
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Content Ideas Dialog -->
    <v-dialog v-model="ideasDialog" max-width="600px">
      <v-card>
        <v-card-title>💡 Идеи для контента</v-card-title>
        <v-card-text>
          <v-form ref="ideasForm">
            <v-textarea
              v-model="ideasData.business_description"
              label="Описание бизнеса *"
              :rules="[rules.required]"
              rows="3"
              density="comfortable"
            />
            <v-select
              v-model="ideasData.platform"
              :items="PLATFORMS"
              item-title="label"
              item-value="value"
              label="Платформа *"
              :rules="[rules.required]"
              density="comfortable"
            />
            <v-text-field
              v-model.number="ideasData.count"
              label="Количество идей"
              type="number"
              min="1"
              max="20"
              density="comfortable"
            />
          </v-form>

          <!-- Ideas List -->
          <v-list v-if="contentIdeas.length" class="mt-4">
            <v-list-item v-for="(idea, idx) in contentIdeas" :key="idx">
              <v-list-item-title>{{ idea.title }}</v-list-item-title>
              <v-list-item-subtitle>{{ idea.description }}</v-list-item-subtitle>
              <template #append>
                <v-btn
                  icon="mdi-plus"
                  variant="text"
                  size="small"
                  @click="createCampaignFromIdea(idea)"
                />
              </template>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="closeIdeasDialog">Закрыть</v-btn>
          <v-btn color="primary" :loading="isLoading" @click="fetchIdeas">
            Получить идеи
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Calendar Dialog -->
    <v-dialog v-model="showCalendar" max-width="900px">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>📅 Календарь контента</span>
          <v-btn icon="mdi-close" variant="text" @click="showCalendar = false" />
        </v-card-title>
        <v-card-text>
          <v-calendar
            v-model="calendarDate"
            :events="calendarEvents"
            color="primary"
            type="month"
          />
          
          <!-- Events List -->
          <v-divider class="my-4" />
          <h3 class="mb-3">Запланированные кампании:</h3>
          <v-list v-if="scheduledCampaigns.length">
            <v-list-item
              v-for="campaign in scheduledCampaigns"
              :key="campaign.id"
              :title="campaign.title"
              :subtitle="`${campaign.scheduled_date ? formatDate(campaign.scheduled_date) : 'Не указано'} - ${campaign.platform}`"
            >
              <template #prepend>
                <v-icon :color="STATUS_COLORS[campaign.status]">
                  mdi-calendar-check
                </v-icon>
              </template>
              <template #append>
                <v-btn
                  icon="mdi-eye"
                  variant="text"
                  size="small"
                  @click="viewCampaign(campaign); showCalendar = false"
                />
              </template>
            </v-list-item>
          </v-list>
          <v-alert v-else type="info" variant="tonal">
            Нет запланированных кампаний
          </v-alert>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMarketingStore } from '@/stores/marketing'
import { storeToRefs } from 'pinia'
import { useNotification } from '@/composables/useNotification'
import StatWidget from '@/components/StatWidget.vue'
import ActionButton from '@/components/ActionButton.vue'
import {
  PLATFORMS,
  CONTENT_TYPES,
  TONES,
  STATUS_LABELS,
  STATUS_COLORS
} from '@/types/marketing'
import type {
  MarketingCampaign,
  MarketingCampaignCreate,
  ContentGenerationRequest,
  ContentGenerationResponse,
  ContentIdea
} from '@/types/marketing'

const marketingStore = useMarketingStore()
const { campaigns, statistics, isLoading } = storeToRefs(marketingStore)
const { show: showNotification } = useNotification()

// Filters
const statusFilter = ref<string>()
const platformFilter = ref<string>()

const statusOptions = [
  { title: 'Черновик', value: 'draft' },
  { title: 'Запланирован', value: 'scheduled' },
  { title: 'Опубликован', value: 'published' },
  { title: 'Архивирован', value: 'archived' }
]

// Table
const headers = [
  { title: 'ID', key: 'id', sortable: true },
  { title: 'Название', key: 'title', sortable: true },
  { title: 'Платформа', key: 'platform', sortable: true },
  { title: 'Тип', key: 'content_type', sortable: true },
  { title: 'Статус', key: 'status', sortable: true },
  { title: 'AI', key: 'ai_generated', sortable: false },
  { title: 'Дата', key: 'scheduled_date', sortable: true },
  { title: 'Действия', key: 'actions', sortable: false }
]

// Dialogs
const campaignDialog = ref(false)
const generatorDialog = ref(false)
const ideasDialog = ref(false)
const showCalendar = ref(false)
const editingCampaign = ref<MarketingCampaign | null>(null)

// Calendar
const calendarDate = ref(new Date())
const scheduledCampaigns = computed(() => 
  campaigns.value.filter(c => c.scheduled_date && c.status === 'scheduled')
)
const calendarEvents = computed(() =>
  scheduledCampaigns.value.map(campaign => ({
    title: campaign.title,
    start: new Date(campaign.scheduled_date!),
    color: STATUS_COLORS[campaign.status] || 'primary'
  }))
)

// Forms
const campaignFormData = ref<MarketingCampaignCreate>({
  title: '',
  status: 'draft'
})

const generatorData = ref<ContentGenerationRequest>({
  title: '',
  platform: 'vk',
  content_type: 'post',
  tone: 'professional',
  length: 'medium',
  include_hashtags: true,
  include_emoji: true
})

const ideasData = ref({
  business_description: '',
  platform: 'vk',
  count: 5
})

const generatedContent = ref<ContentGenerationResponse | null>(null)
const contentIdeas = ref<ContentIdea[]>([])

const rules = {
  required: (v: any) => !!v || 'Обязательное поле'
}

// Methods
const loadCampaigns = async () => {
  try {
    await marketingStore.fetchCampaigns({
      status: statusFilter.value,
      platform: platformFilter.value
    })
    await marketingStore.fetchStatistics()
  } catch (error) {
    showNotification('Ошибка загрузки кампаний', 'error')
  }
}

const applyFilters = () => {
  loadCampaigns()
}

const openCreateDialog = () => {
  editingCampaign.value = null
  campaignFormData.value = { title: '', status: 'draft' }
  campaignDialog.value = true
}

const editCampaign = (campaign: MarketingCampaign) => {
  editingCampaign.value = campaign
  campaignFormData.value = {
    title: campaign.title,
    description: campaign.description,
    content: campaign.content,
    platform: campaign.platform,
    content_type: campaign.content_type,
    target_audience: campaign.target_audience,
    tags: campaign.tags,
    scheduled_date: campaign.scheduled_date,
    status: campaign.status
  }
  campaignDialog.value = true
}

const viewCampaign = (campaign: MarketingCampaign) => {
  // TODO: Implement campaign detail view
  showNotification(`Просмотр кампании: ${campaign.title}`, 'info')
}

const saveCampaign = async () => {
  try {
    if (editingCampaign.value) {
      await marketingStore.updateCampaign(editingCampaign.value.id, campaignFormData.value)
      showNotification('Кампания обновлена', 'success')
    } else {
      await marketingStore.createCampaign(campaignFormData.value)
      showNotification('Кампания создана', 'success')
    }
    closeCampaignDialog()
  } catch (error) {
    showNotification('Ошибка сохранения', 'error')
  }
}

const closeCampaignDialog = () => {
  campaignDialog.value = false
  editingCampaign.value = null
}

const confirmDelete = async (id: number) => {
  if (confirm('Удалить кампанию?')) {
    try {
      await marketingStore.deleteCampaign(id)
      showNotification('Кампания удалена', 'success')
    } catch (error) {
      showNotification('Ошибка удаления', 'error')
    }
  }
}

const publishCampaignAction = async (id: number) => {
  try {
    await marketingStore.publishCampaign(id)
    showNotification('Кампания опубликована', 'success')
  } catch (error) {
    showNotification('Ошибка публикации', 'error')
  }
}

const openGeneratorDialog = () => {
  generatorData.value = {
    title: '',
    platform: 'vk',
    content_type: 'post',
    tone: 'professional',
    length: 'medium',
    include_hashtags: true,
    include_emoji: true
  }
  generatedContent.value = null
  generatorDialog.value = true
}

const closeGeneratorDialog = () => {
  generatorDialog.value = false
  generatedContent.value = null
}

const generateContentAction = async () => {
  try {
    generatedContent.value = await marketingStore.generateContent(generatorData.value)
    showNotification('Контент сгенерирован!', 'success')
  } catch (error) {
    showNotification('Ошибка генерации', 'error')
  }
}

const createCampaignFromGenerated = () => {
  if (!generatedContent.value) return
  
  campaignFormData.value = {
    title: generatorData.value.title,
    content: generatedContent.value.content,
    platform: generatorData.value.platform,
    content_type: generatorData.value.content_type,
    target_audience: generatorData.value.target_audience,
    tags: generatedContent.value.hashtags || [],
    status: 'draft'
  }
  
  closeGeneratorDialog()
  campaignDialog.value = true
}

const openIdeasDialog = () => {
  ideasData.value = {
    business_description: '',
    platform: 'vk',
    count: 5
  }
  contentIdeas.value = []
  ideasDialog.value = true
}

const closeIdeasDialog = () => {
  ideasDialog.value = false
  contentIdeas.value = []
}

const fetchIdeas = async () => {
  try {
    const response = await marketingStore.getContentIdeas(ideasData.value)
    contentIdeas.value = response.ideas
    showNotification('Идеи получены!', 'success')
  } catch (error) {
    showNotification('Ошибка получения идей', 'error')
  }
}

const createCampaignFromIdea = (idea: ContentIdea) => {
  campaignFormData.value = {
    title: idea.title,
    description: idea.description,
    content_type: idea.content_type,
    platform: ideasData.value.platform,
    tags: idea.suggested_hashtags,
    status: 'draft'
  }
  
  closeIdeasDialog()
  campaignDialog.value = true
}

const getPlatformIcon = (platform?: string) => {
  const icons: Record<string, string> = {
    vk: 'mdi-vk',
    telegram: 'mdi-telegram',
    instagram: 'mdi-instagram',
    facebook: 'mdi-facebook'
  }
  return icons[platform || ''] || 'mdi-web'
}

const getPlatformColor = (platform?: string) => {
  const colors: Record<string, string> = {
    vk: 'blue',
    telegram: 'cyan',
    instagram: 'pink',
    facebook: 'indigo'
  }
  return colors[platform || ''] || 'grey'
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('ru-RU')
}

onMounted(() => {
  loadCampaigns()
})
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
