<template>
  <div class="auth-view">
    <v-container>
      <v-row justify="center">
        <v-col cols="12" sm="8" md="6" lg="4">
          <v-card class="auth-card elevation-8">
            <v-card-title class="text-h4 mb-4 text-center">
              <span class="alfa-logo">Alfa</span> Copilot
            </v-card-title>
            
            <!-- Magic Link Step -->
            <v-card-text v-if="!magicLinkSent && !verifyingToken">
              <p class="text-body-1 mb-6 text-center">
                Введите email для получения ссылки для входа
              </p>
              
              <v-alert v-if="authStore.error" type="error" class="mb-4" closable @click:close="authStore.clearError()">
                {{ authStore.error }}
              </v-alert>

              <v-form @submit.prevent="handleSendMagicLink">
                <v-text-field
                  v-model="email"
                  label="Email"
                  type="email"
                  variant="outlined"
                  :disabled="authStore.loading"
                  :rules="[rules.required, rules.email]"
                  prepend-inner-icon="mdi-email"
                  class="mb-4"
                ></v-text-field>
                
                <v-btn
                  color="primary"
                  block
                  size="large"
                  type="submit"
                  :loading="authStore.loading"
                >
                  Отправить ссылку
                </v-btn>
              </v-form>
            </v-card-text>

            <!-- Success Message -->
            <v-card-text v-if="magicLinkSent" class="text-center">
              <v-icon color="success" size="64" class="mb-4">mdi-email-check</v-icon>
              <p class="text-h6 mb-2">Письмо отправлено!</p>
              <p class="text-body-2 text-medium-emphasis">
                Проверьте почту <strong>{{ email }}</strong> и перейдите по ссылке для входа
              </p>
              <v-btn
                variant="text"
                color="primary"
                class="mt-4"
                @click="resetForm"
              >
                Отправить на другой email
              </v-btn>
            </v-card-text>

            <!-- Verifying Token -->
            <v-card-text v-if="verifyingToken" class="text-center">
              <v-progress-circular
                indeterminate
                color="primary"
                size="64"
                class="mb-4"
              ></v-progress-circular>
              <p class="text-h6">Проверка...</p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const magicLinkSent = ref(false)
const verifyingToken = ref(false)

const rules = {
  required: (value: string) => !!value || 'Поле обязательно',
  email: (value: string) => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return pattern.test(value) || 'Неверный формат email'
  }
}

const handleSendMagicLink = async () => {
  if (!email.value) return

  const success = await authStore.loginWithMagicLink(email.value)
  if (success) {
    magicLinkSent.value = true
  }
}

const resetForm = () => {
  email.value = ''
  magicLinkSent.value = false
  authStore.clearError()
}

const verifyToken = async (token: string) => {
  verifyingToken.value = true
  const success = await authStore.loginWithToken(token)
  
  if (success) {
    // Redirect to original page or home
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } else {
    verifyingToken.value = false
  }
}

// Check for token in URL on mount
onMounted(() => {
  const token = route.query.token as string
  if (token) {
    verifyToken(token)
  }
})
</script>

<style scoped>
.auth-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, var(--v-theme-background) 0%, var(--v-theme-surface) 100%);
}

.auth-card {
  padding: 32px;
  border-radius: 16px;
}

.alfa-logo {
  color: var(--v-theme-primary);
  font-weight: 700;
}
</style>
