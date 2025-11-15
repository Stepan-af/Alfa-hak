import { defineStore } from 'pinia'
import { ref } from 'vue'
import { documentsAPI } from '@/api/documents'
import type { Template, Document, DocumentCreate, GenerateDocumentRequest } from '@/types/documents'

export const useDocumentsStore = defineStore('documents', () => {
  const templates = ref<Template[]>([])
  const documents = ref<Document[]>([])
  const currentDocument = ref<Document | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchTemplates() {
    try {
      loading.value = true
      templates.value = await documentsAPI.getTemplates()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки шаблонов'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchDocuments() {
    try {
      loading.value = true
      documents.value = await documentsAPI.getDocuments()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки документов'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createDocument(data: DocumentCreate) {
    try {
      loading.value = true
      const doc = await documentsAPI.createDocument(data)
      documents.value.unshift(doc)
      return doc
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка создания документа'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function generateDocument(data: GenerateDocumentRequest) {
    try {
      loading.value = true
      const result = await documentsAPI.generateDocument(data)
      await fetchDocuments() // Refresh list
      return result
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка генерации документа'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteDocument(id: number) {
    try {
      loading.value = true
      await documentsAPI.deleteDocument(id)
      documents.value = documents.value.filter(d => d.id !== id)
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Ошибка удаления документа'
      throw e
    } finally {
      loading.value = false
    }
  }

  function $reset() {
    templates.value = []
    documents.value = []
    currentDocument.value = null
    loading.value = false
    error.value = null
  }

  return {
    templates,
    documents,
    currentDocument,
    loading,
    error,
    fetchTemplates,
    fetchDocuments,
    createDocument,
    generateDocument,
    deleteDocument,
    $reset,
  }
})
