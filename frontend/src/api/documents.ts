import apiClient from './client'
import type {
  Template,
  Document,
  DocumentCreate,
  DocumentUpdate,
  GenerateDocumentRequest,
  GenerateDocumentResponse,
} from '@/types/documents'

export const documentsAPI = {
  // Templates
  getTemplates(params?: {
    category?: string
    document_type?: string
    include_user?: boolean
  }): Promise<Template[]> {
    return apiClient.get('/documents/templates', { params })
  },

  getTemplate(id: number): Promise<Template> {
    return apiClient.get(`/documents/templates/${id}`)
  },

  // Documents
  getDocuments(params?: {
    document_type?: string
    status?: string
    limit?: number
    offset?: number
  }): Promise<Document[]> {
    return apiClient.get('/documents/', { params })
  },

  getDocument(id: number): Promise<Document> {
    return apiClient.get(`/documents/${id}`)
  },

  createDocument(data: DocumentCreate): Promise<Document> {
    return apiClient.post('/documents/', data)
  },

  updateDocument(id: number, data: DocumentUpdate): Promise<Document> {
    return apiClient.put(`/documents/${id}`, data)
  },

  deleteDocument(id: number): Promise<void> {
    return apiClient.delete(`/documents/${id}`)
  },

  // Generation
  generateDocument(data: GenerateDocumentRequest): Promise<GenerateDocumentResponse> {
    return apiClient.post('/documents/generate', data)
  },

  // Initialize templates
  initTemplates(): Promise<{created: number, message: string}> {
    return apiClient.post('/documents/init-templates')
  },
}
