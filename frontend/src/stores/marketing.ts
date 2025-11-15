import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as marketingApi from '@/api/marketing'
import type {
  MarketingCampaign,
  MarketingCampaignCreate,
  MarketingCampaignUpdate,
  ContentGenerationRequest,
  ContentGenerationResponse,
  ContentIdeasRequest,
  ContentIdeasResponse,
  CampaignStatistics,
  ContentCalendar
} from '@/types/marketing'

export const useMarketingStore = defineStore('marketing', () => {
  // State
  const campaigns = ref<MarketingCampaign[]>([])
  const currentCampaign = ref<MarketingCampaign | null>(null)
  const statistics = ref<CampaignStatistics | null>(null)
  const calendar = ref<ContentCalendar | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const draftCampaigns = computed(() =>
    campaigns.value.filter((c) => c.status === 'draft')
  )

  const scheduledCampaigns = computed(() =>
    campaigns.value.filter((c) => c.status === 'scheduled')
  )

  const publishedCampaigns = computed(() =>
    campaigns.value.filter((c) => c.status === 'published')
  )

  const aiGeneratedCampaigns = computed(() =>
    campaigns.value.filter((c) => c.ai_generated === 'true')
  )

  const campaignsByPlatform = computed(() => {
    const grouped: Record<string, MarketingCampaign[]> = {}
    campaigns.value.forEach((c) => {
      if (c.platform) {
        if (!grouped[c.platform]) {
          grouped[c.platform] = []
        }
        grouped[c.platform].push(c)
      }
    })
    return grouped
  })

  // Actions
  const fetchCampaigns = async (filters?: {
    status?: string
    platform?: string
    skip?: number
    limit?: number
  }) => {
    isLoading.value = true
    error.value = null
    try {
      campaigns.value = await marketingApi.getCampaigns(filters)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch campaigns'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const fetchCampaign = async (campaignId: number) => {
    isLoading.value = true
    error.value = null
    try {
      currentCampaign.value = await marketingApi.getCampaign(campaignId)
      return currentCampaign.value
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch campaign'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const createCampaign = async (data: MarketingCampaignCreate) => {
    isLoading.value = true
    error.value = null
    try {
      const campaign = await marketingApi.createCampaign(data)
      campaigns.value.unshift(campaign)
      return campaign
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to create campaign'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const updateCampaign = async (campaignId: number, data: MarketingCampaignUpdate) => {
    isLoading.value = true
    error.value = null
    try {
      const campaign = await marketingApi.updateCampaign(campaignId, data)
      const index = campaigns.value.findIndex((c) => c.id === campaignId)
      if (index !== -1) {
        campaigns.value[index] = campaign
      }
      if (currentCampaign.value?.id === campaignId) {
        currentCampaign.value = campaign
      }
      return campaign
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to update campaign'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const deleteCampaign = async (campaignId: number) => {
    isLoading.value = true
    error.value = null
    try {
      await marketingApi.deleteCampaign(campaignId)
      campaigns.value = campaigns.value.filter((c) => c.id !== campaignId)
      if (currentCampaign.value?.id === campaignId) {
        currentCampaign.value = null
      }
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to delete campaign'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const generateContent = async (
    request: ContentGenerationRequest
  ): Promise<ContentGenerationResponse> => {
    isLoading.value = true
    error.value = null
    try {
      return await marketingApi.generateContent(request)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to generate content'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const getContentIdeas = async (request: ContentIdeasRequest): Promise<ContentIdeasResponse> => {
    isLoading.value = true
    error.value = null
    try {
      return await marketingApi.getContentIdeas(request)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to get content ideas'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const fetchStatistics = async () => {
    isLoading.value = true
    error.value = null
    try {
      statistics.value = await marketingApi.getStatistics()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch statistics'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const fetchCalendar = async (month: number, year: number) => {
    isLoading.value = true
    error.value = null
    try {
      calendar.value = await marketingApi.getContentCalendar(month, year)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to fetch calendar'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const publishCampaign = async (campaignId: number) => {
    isLoading.value = true
    error.value = null
    try {
      const campaign = await marketingApi.publishCampaign(campaignId)
      const index = campaigns.value.findIndex((c) => c.id === campaignId)
      if (index !== -1) {
        campaigns.value[index] = campaign
      }
      if (currentCampaign.value?.id === campaignId) {
        currentCampaign.value = campaign
      }
      return campaign
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Failed to publish campaign'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    campaigns,
    currentCampaign,
    statistics,
    calendar,
    isLoading,
    error,
    // Computed
    draftCampaigns,
    scheduledCampaigns,
    publishedCampaigns,
    aiGeneratedCampaigns,
    campaignsByPlatform,
    // Actions
    fetchCampaigns,
    fetchCampaign,
    createCampaign,
    updateCampaign,
    deleteCampaign,
    generateContent,
    getContentIdeas,
    fetchStatistics,
    fetchCalendar,
    publishCampaign
  }
})
