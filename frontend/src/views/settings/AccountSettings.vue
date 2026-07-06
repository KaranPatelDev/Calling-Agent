<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
      >
        <h1 class="text-2xl font-bold text-gray-900">Account Settings</h1>
        <p class="text-sm text-gray-500 mt-1">Manage your profile and Exotel configuration</p>
      </motion.div>

      <div v-if="!user" class="space-y-4">
        <div class="skeleton h-10 w-full max-w-2xl"></div>
        <div class="skeleton h-10 w-full max-w-2xl"></div>
        <div class="skeleton h-10 w-full max-w-2xl"></div>
      </div>

      <motion.form
        v-else
        @submit.prevent="handleSave"
        initial="{ opacity: 0, y: 10 }"
        animate="{ opacity: 1, y: 0 }"
        transition="{ delay: 0.1 }"
        class="card max-w-2xl space-y-6"
      >
        <div>
          <h2 class="text-lg font-semibold text-gray-900">Profile</h2>
          <p class="text-sm text-gray-500 mt-1">Your basic account information</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Full Name</label>
            <input v-model="form.full_name" type="text" class="input-field" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Phone</label>
            <input v-model="form.phone" type="tel" class="input-field" placeholder="+91XXXXXXXXXX" />
          </div>
        </div>

        <div class="pt-4 border-t border-gray-100">
          <h2 class="text-lg font-semibold text-gray-900">Exotel Configuration</h2>
          <p class="text-sm text-gray-500 mt-1">Enter your Exotel API credentials to enable outbound calling</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Account SID</label>
            <input v-model="form.exotel_account_sid" type="text" class="input-field" placeholder="ACxxxxxxxx" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">API Key</label>
            <input v-model="form.exotel_api_key" type="text" class="input-field" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">API Token</label>
            <input v-model="form.exotel_api_token" type="password" class="input-field" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Caller ID (140-series)</label>
            <input v-model="form.exotel_caller_id" type="tel" class="input-field" placeholder="0123456789" />
          </div>
        </div>

        <div class="pt-4 border-t border-gray-100">
          <h2 class="text-lg font-semibold text-gray-900">Preferences</h2>
        </div>
        <div class="max-w-xs">
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Timezone</label>
          <select v-model="form.timezone" class="input-field">
            <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
            <option value="Asia/Dubai">Asia/Dubai (GST)</option>
            <option value="UTC">UTC</option>
          </select>
        </div>

        <transition name="fade">
          <div v-if="success" class="flex items-center gap-2 p-3 rounded-xl bg-emerald-50 border border-emerald-100">
            <CheckCircle :size="16" class="text-emerald-500" />
            <p class="text-sm text-emerald-700">Settings saved successfully!</p>
          </div>
        </transition>
        <transition name="fade">
          <div v-if="error" class="flex items-center gap-2 p-3 rounded-xl bg-red-50 border border-red-100">
            <AlertCircle :size="16" class="text-red-500" />
            <p class="text-sm text-red-600">{{ error }}</p>
          </div>
        </transition>

        <button type="submit" :disabled="saving" class="btn-primary flex items-center gap-2">
          <Loader2 v-if="saving" :size="16" class="animate-spin" />
          {{ saving ? 'Saving...' : 'Save Settings' }}
        </button>
      </motion.form>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { motion } from 'motion-v'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { CheckCircle, AlertCircle, Loader2 } from '@lucide/vue'

const authStore = useAuthStore()
const { user } = authStore

const form = reactive({
  full_name: '',
  phone: '',
  exotel_account_sid: '',
  exotel_api_key: '',
  exotel_api_token: '',
  exotel_caller_id: '',
  timezone: 'Asia/Kolkata',
})

const saving = ref(false)
const success = ref(false)
const error = ref('')

onMounted(() => {
  if (user) {
    Object.assign(form, {
      full_name: user.full_name || '',
      phone: user.phone || '',
      exotel_account_sid: user.exotel_account_sid || '',
      exotel_api_key: user.exotel_api_key || '',
      exotel_api_token: user.exotel_api_token || '',
      exotel_caller_id: user.exotel_caller_id || '',
      timezone: user.timezone || 'Asia/Kolkata',
    })
  }
})

async function handleSave() {
  saving.value = true
  success.value = false
  error.value = ''
  try {
    await authStore.updateProfile(form)
    success.value = true
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to save settings'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: all 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
