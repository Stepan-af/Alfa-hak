// Types for Documents module

export interface Template {
  id: number
  name: string
  description?: string
  content: string
  category?: string
  document_type?: string
  variables?: Record<string, VariableDefinition>
  is_system: boolean
  user_id?: number
  usage_count: number
  created_at: string
  updated_at?: string
}

export interface VariableDefinition {
  type: string
  required: boolean
  default: string
}

export interface Document {
  id: number
  user_id: number
  title: string
  content?: string
  template_id?: number
  document_type?: string
  variables?: Record<string, any>
  file_path?: string
  file_format: string
  status: 'draft' | 'final' | 'signed' | 'archived'
  version: number
  counterparty_name?: string
  counterparty_inn?: string
  amount?: string
  currency: string
  ai_generated?: string
  created_at: string
  updated_at?: string
}

export interface DocumentCreate {
  title: string
  content?: string
  template_id?: number
  document_type?: string
  variables?: Record<string, any>
  counterparty_name?: string
  counterparty_inn?: string
  amount?: string
  currency?: string
}

export interface DocumentUpdate {
  title?: string
  content?: string
  document_type?: string
  variables?: Record<string, any>
  status?: 'draft' | 'final' | 'signed' | 'archived'
  counterparty_name?: string
  counterparty_inn?: string
  amount?: string
  currency?: string
}

export interface GenerateDocumentRequest {
  template_id: number
  title: string
  variables: Record<string, any>
  document_type?: string
  counterparty_name?: string
  counterparty_inn?: string
  amount?: string
}

export interface GenerateDocumentResponse {
  document_id: number
  title: string
  content: string
  file_path?: string
}
