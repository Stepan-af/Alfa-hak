// === Base Campaign Types ===
export interface MarketingCampaign {
  id: number
  user_id: number
  title: string
  description?: string
  content?: string
  platform?: string // "vk" | "telegram" | "instagram" | "facebook"
  content_type?: string // "post" | "story" | "ad" | "newsletter"
  target_audience?: string
  tags?: string[]
  scheduled_date?: string // ISO date
  published_date?: string // ISO datetime
  status: string // "draft" | "scheduled" | "published" | "archived"
  ai_prompt?: string
  ai_generated: string // "true" | "false"
  views: number
  likes: number
  shares: number
  created_at: string
  updated_at: string
}

export interface MarketingCampaignCreate {
  title: string
  description?: string
  content?: string
  platform?: string
  content_type?: string
  target_audience?: string
  tags?: string[]
  scheduled_date?: string
  status?: string
}

export interface MarketingCampaignUpdate {
  title?: string
  description?: string
  content?: string
  platform?: string
  content_type?: string
  target_audience?: string
  tags?: string[]
  scheduled_date?: string
  status?: string
}

// === AI Content Generation ===
export interface ContentGenerationRequest {
  title: string
  platform: string
  content_type: string
  target_audience?: string
  tone?: string // "professional" | "casual" | "friendly" | "formal"
  keywords?: string[]
  length?: string // "short" | "medium" | "long"
  include_hashtags?: boolean
  include_emoji?: boolean
  additional_instructions?: string
}

export interface ContentGenerationResponse {
  content: string
  hashtags?: string[]
  suggested_title?: string
  ai_prompt: string
}

export interface ContentIdeasRequest {
  business_description: string
  platform: string
  count?: number // 1-20
}

export interface ContentIdea {
  title: string
  description: string
  content_type: string
  suggested_hashtags: string[]
}

export interface ContentIdeasResponse {
  ideas: ContentIdea[]
}

// === Analytics & Metrics ===
export interface CampaignMetrics {
  campaign_id: number
  views: number
  likes: number
  shares: number
  engagement_rate: number
}

export interface CampaignStatistics {
  total_campaigns: number
  draft_campaigns: number
  scheduled_campaigns: number
  published_campaigns: number
  archived_campaigns: number
  total_views: number
  total_likes: number
  total_shares: number
  average_engagement_rate: number
  campaigns_by_platform: Record<string, number>
}

// === Content Calendar ===
export interface CalendarEntry {
  campaign_id: number
  title: string
  platform: string
  scheduled_date: string
  status: string
}

export interface ContentCalendar {
  month: number
  year: number
  entries: CalendarEntry[]
}

// === Platform-specific Types ===
export interface InstagramPostRequest {
  caption: string
  hashtags?: string[]
  location?: string
  mentions?: string[]
}

export interface VKPostRequest {
  message: string
  attachments?: string[]
  tags?: string[]
}

export interface TelegramPostRequest {
  text: string
  parse_mode?: string // "Markdown" | "HTML"
  disable_web_page_preview?: boolean
}

// === UI Helper Types ===
export interface PlatformOption {
  value: string
  label: string
  icon: string
}

export interface ContentTypeOption {
  value: string
  label: string
  description: string
}

export interface ToneOption {
  value: string
  label: string
}

export const PLATFORMS: PlatformOption[] = [
  { value: 'vk', label: 'ВКонтакте', icon: 'mdi-vk' },
  { value: 'telegram', label: 'Telegram', icon: 'mdi-telegram' },
  { value: 'instagram', label: 'Instagram', icon: 'mdi-instagram' },
  { value: 'facebook', label: 'Facebook', icon: 'mdi-facebook' }
]

export const CONTENT_TYPES: ContentTypeOption[] = [
  { value: 'post', label: 'Пост', description: 'Обычная публикация' },
  { value: 'story', label: 'История', description: 'Временный контент' },
  { value: 'ad', label: 'Реклама', description: 'Рекламное объявление' },
  { value: 'newsletter', label: 'Рассылка', description: 'Email/Telegram рассылка' }
]

export const TONES: ToneOption[] = [
  { value: 'professional', label: 'Профессиональный' },
  { value: 'casual', label: 'Неформальный' },
  { value: 'friendly', label: 'Дружелюбный' },
  { value: 'formal', label: 'Официальный' }
]

export const STATUS_LABELS: Record<string, string> = {
  draft: 'Черновик',
  scheduled: 'Запланирован',
  published: 'Опубликован',
  archived: 'Архивирован'
}

export const STATUS_COLORS: Record<string, string> = {
  draft: 'grey',
  scheduled: 'blue',
  published: 'green',
  archived: 'orange'
}
