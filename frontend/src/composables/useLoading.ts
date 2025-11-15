import { ref, computed } from 'vue'

interface LoadingState {
  [key: string]: boolean
}

const loadingStates = ref<LoadingState>({})

export const useLoading = (key: string = 'default') => {
  const isLoading = computed(() => loadingStates.value[key] || false)

  const start = () => {
    loadingStates.value[key] = true
  }

  const stop = () => {
    loadingStates.value[key] = false
  }

  const toggle = () => {
    loadingStates.value[key] = !loadingStates.value[key]
  }

  // Wrap async function with loading state
  const withLoading = async <T>(fn: () => Promise<T>): Promise<T> => {
    try {
      start()
      return await fn()
    } finally {
      stop()
    }
  }

  return {
    isLoading,
    start,
    stop,
    toggle,
    withLoading
  }
}

// Global loading state for app-wide loading indicator
export const useGlobalLoading = () => useLoading('global')
