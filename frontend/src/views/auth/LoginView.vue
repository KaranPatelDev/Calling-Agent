<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-white to-brand-50/30 px-4">
    <motion.div
      initial="{ opacity: 0, y: 20, scale: 0.98 }"
      animate="{ opacity: 1, y: 0, scale: 1 }"
      transition="{ duration: 0.4 }"
      class="w-full max-w-md"
    >
      <div class="text-center mb-8">
        <router-link to="/" class="inline-flex items-center gap-2 mb-6">
          <div class="w-10 h-10 bg-gradient-to-br from-brand-500 to-purple-600 rounded-xl flex items-center justify-center">
            <Phone :size="20" class="text-white" />
          </div>
          <span class="text-xl font-bold gradient-text">Calling Agent</span>
        </router-link>
        <h1 class="text-2xl font-bold text-gray-900">Welcome back</h1>
        <p class="text-gray-500 mt-1">Sign in to your account</p>
      </div>

      <div class="card">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
            <input v-model="form.email" type="email" required class="input-field" placeholder="you@example.com" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
            <input v-model="form.password" type="password" required class="input-field" placeholder="Enter your password" />
          </div>

          <transition name="fade">
            <div v-if="error" class="flex items-center gap-2 p-3 rounded-xl bg-red-50 border border-red-100">
              <AlertCircle :size="16" class="text-red-500 shrink-0" />
              <p class="text-sm text-red-600">{{ error }}</p>
            </div>
          </transition>

          <button type="submit" :disabled="loading" class="btn-primary w-full flex items-center justify-center gap-2">
            <Loader2 v-if="loading" :size="18" class="animate-spin" />
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>
      </div>

      <p class="mt-6 text-center text-sm text-gray-600">
        Don't have an account?
        <router-link to="/register" class="text-brand-600 hover:text-brand-700 font-medium">Create one free</router-link>
      </p>
    </motion.div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { motion } from 'motion-v'
import { Phone, AlertCircle, Loader2 } from '@lucide/vue'

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
