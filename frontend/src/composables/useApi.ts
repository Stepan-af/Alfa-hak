import { ref } from 'vue'
import { useNotification } from './useNotification'
import { useLoading } from './useLoading'

interface ApiOptions {
  showLoading?: boolean
  showError?: boolean
  showSuccess?: boolean
  successMessage?: string
  loadingKey?: string
}

export const useApi = <T = any>(options: ApiOptions = {}) => {
  const {
    showLoading = true,
    showError = true,
    showSuccess = false,
    successMessage,
    loadingKey = 'api'
  } = options

  const notification = useNotification()
  const loading = useLoading(loadingKey)

  const data = ref<T | null>(null)
  const error = ref<Error | null>(null)
  const isLoading = loading.isLoading

  const execute = async (apiCall: () => Promise<T>): Promise<T | null> => {
    try {
      error.value = null
      
      if (showLoading) {
        loading.start()
      }

      const result = await apiCall()
      data.value = result

      if (showSuccess && successMessage) {
        notification.success(successMessage)
      }

      return result
    } catch (err: any) {
      error.value = err
      
      if (showError) {
        const errorMessage = err?.detail || err?.message || 'Произошла ошибка'
        notification.error(errorMessage)
      }

      return null
    } finally {
      if (showLoading) {
        loading.stop()
      }
    }
  }

  const reset = () => {
    data.value = null
    error.value = null
  }

  return {
    data,
    error,
    isLoading,
    execute,
    reset
  }
}
