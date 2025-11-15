import apiClient from './client'
import type {
  MarketingCampaign,
  MarketingCampaignCreate,
  MarketingCampaignUpdate,
  ContentGenerationRequest,
  ContentGenerationResponse,
  ContentIdeasRequest,
  ContentIdeasResponse,
  CampaignMetrics,
  CampaignStatistics,
  ContentCalendar
} from '@/types/marketing'

// === Campaign CRUD ===

export const createCampaign = async (data: MarketingCampaignCreate): Promise<MarketingCampaign> => {
  const response = await apiClient.post('/marketing/campaigns', data)
  return response.data
}

export const getCampaigns = async (params?: {
  status?: string
  platform?: string
  skip?: number
  limit?: number
}): Promise<MarketingCampaign[]> => {
  const response = await apiClient.get('/marketing/campaigns', { params })
  return response.data
}

export const getCampaign = async (campaignId: number): Promise<MarketingCampaign> => {
  const response = await apiClient.get(`/marketing/campaigns/${campaignId}`)
  return response.data
}

export const updateCampaign = async (
  campaignId: number,
  data: MarketingCampaignUpdate
): Promise<MarketingCampaign> => {
  const response = await apiClient.put(`/marketing/campaigns/${campaignId}`, data)
  return response.data
}

export const deleteCampaign = async (campaignId: number): Promise<void> => {
  await apiClient.delete(`/marketing/campaigns/${campaignId}`)
}

// === AI Content Generation ===

export const generateContent = async (
  data: ContentGenerationRequest
): Promise<ContentGenerationResponse> => {
  const response = await apiClient.post('/marketing/generate-content', data)
  return response.data
}

export const getContentIdeas = async (
  data: ContentIdeasRequest
): Promise<ContentIdeasResponse> => {
  const response = await apiClient.post('/marketing/content-ideas', data)
  return response.data
}

// === Analytics ===

export const getCampaignMetrics = async (campaignId: number): Promise<CampaignMetrics> => {
  const response = await apiClient.get(`/marketing/campaigns/${campaignId}/metrics`)
  return response.data
}

export const getStatistics = async (): Promise<CampaignStatistics> => {
  const response = await apiClient.get('/marketing/statistics')
  return response.data
}

// === Content Calendar ===

export const getContentCalendar = async (month: number, year: number): Promise<ContentCalendar> => {
  const response = await apiClient.get('/marketing/calendar', {
    params: { month, year }
  })
  return response.data
}

// === Publishing ===

export const publishCampaign = async (campaignId: number): Promise<MarketingCampaign> => {
  const response = await apiClient.post(`/marketing/campaigns/${campaignId}/publish`)
  return response.data
}
