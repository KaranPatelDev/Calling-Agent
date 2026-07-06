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
        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">Create your account</h1>
        <p class="text-surface-500 mt-1">Start making automated calls in minutes</p>
      </div>

      <div class="card">
        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Full Name</label>
            <InputText v-model="form.full_name" type="text" required class="w-full" placeholder="John Doe" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Email</label>
            <InputText v-model="form.email" type="email" required class="w-full" placeholder="you@example.com" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Phone</label>
            <InputText v-model="form.phone" type="tel" class="w-full" placeholder="+91XXXXXXXXXX" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Password</label>
            <Password v-model="form.password" required :minlength="6" :feedback="false" toggle-mask class="w-full" input-class="w-full" placeholder="Min. 6 characters" />
          </div>

          <transition name="fade">
            <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>
          </transition>

          <Button type="submit" :loading="loading" :label="loading ? 'Creating account...' : 'Create Account'" class="w-full" />
        </form>
      </div>

      <p class="mt-6 text-center text-sm text-surface-600 dark:text-surface-400">
        Already have an account?
        <router-link to="/login" class="text-primary-600 hover:text-primary-700 font-medium">Sign in</router-link>
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
const form = ref({ full_name: '', email: '', phone: '', password: '' })
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  loading.value = true
  error.value = ''
  try {
    await authStore.register(form.value)
    await authStore.login(form.value.email, form.value.password)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: all 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
