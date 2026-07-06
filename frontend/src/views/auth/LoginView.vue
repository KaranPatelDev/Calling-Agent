<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-surface-50 via-surface-0 to-primary-50/30 dark:from-surface-950 dark:via-surface-950 dark:to-primary-950/30 px-4">
    <motion.div
      initial="{ opacity: 0, y: 20, scale: 0.98 }"
      animate="{ opacity: 1, y: 0, scale: 1 }"
      transition="{ duration: 0.4 }"
      class="w-full max-w-md"
    >
      <div class="text-center mb-8">
        <router-link to="/" class="inline-flex items-center gap-2 mb-6">
          <div class="w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl flex items-center justify-center">
            <Phone :size="20" class="text-white" />
          </div>
          <span class="text-xl font-bold gradient-text">Calling Agent</span>
        </router-link>
        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">Welcome back</h1>
        <p class="text-surface-500 mt-1">Sign in to your account</p>
      </div>

      <div class="card">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Email</label>
            <InputText v-model="form.email" type="email" required class="w-full" placeholder="you@example.com" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Password</label>
            <Password v-model="form.password" required :feedback="false" toggle-mask class="w-full" input-class="w-full" placeholder="Enter your password" />
          </div>

          <transition name="fade">
            <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>
          </transition>

          <Button type="submit" :loading="loading" :label="loading ? 'Signing in...' : 'Sign In'" class="w-full" />
        </form>
      </div>

      <p class="mt-6 text-center text-sm text-surface-600 dark:text-surface-400">
        Don't have an account?
        <router-link to="/register" class="text-primary-600 hover:text-primary-700 font-medium">Create one free</router-link>
      </p>
    </motion.div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { motion } from 'motion-v'
import { Phone } from '@lucide/vue'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

const authStore = useAuthStore()
const router = useRouter()
const form = ref({ email: '', password: '' })
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await authStore.login(form.value.email, form.value.password)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: all 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
