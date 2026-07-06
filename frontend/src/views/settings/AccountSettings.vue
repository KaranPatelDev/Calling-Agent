<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
      >
        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">Account Settings</h1>
        <p class="text-sm text-surface-500 mt-1">Manage your profile and Exotel configuration</p>
      </motion.div>

      <div v-if="!user" class="space-y-4 max-w-2xl">
        <Skeleton height="2.5rem" />
        <Skeleton height="2.5rem" />
        <Skeleton height="2.5rem" />
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
          <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-0">Profile</h2>
          <p class="text-sm text-surface-500 mt-1">Your basic account information</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Full Name</label>
            <InputText v-model="form.full_name" class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Phone</label>
            <InputText v-model="form.phone" type="tel" class="w-full" placeholder="+91XXXXXXXXXX" />
          </div>
        </div>

        <div class="pt-4 border-t border-surface-100 dark:border-surface-700">
          <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-0">Exotel Configuration</h2>
          <p class="text-sm text-surface-500 mt-1">Enter your Exotel API credentials to enable outbound calling</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Account SID</label>
            <InputText v-model="form.exotel_account_sid" class="w-full" placeholder="ACxxxxxxxx" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">API Key</label>
            <InputText v-model="form.exotel_api_key" class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">API Token</label>
            <Password v-model="form.exotel_api_token" :feedback="false" toggle-mask class="w-full" input-class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Caller ID (140-series)</label>
            <InputText v-model="form.exotel_caller_id" type="tel" class="w-full" placeholder="0123456789" />
          </div>
        </div>

        <div class="pt-4 border-t border-surface-100 dark:border-surface-700">
          <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-0">Preferences</h2>
        </div>
        <div class="max-w-xs">
          <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Timezone</label>
          <Select v-model="form.timezone" :options="timezoneOptions" option-label="label" option-value="value" class="w-full" />
        </div>

        <transition name="fade">
          <Message v-if="success" severity="success" :closable="false">Settings saved successfully!</Message>
        </transition>
        <transition name="fade">
          <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>
        </transition>

        <Button type="submit" :loading="saving" :label="saving ? 'Saving...' : 'Save Settings'" />
      </motion.form>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { motion } from 'motion-v'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Skeleton from 'primevue/skeleton'

const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const timezoneOptions = [
  { label: 'Asia/Kolkata (IST)', value: 'Asia/Kolkata' },
  { label: 'Asia/Dubai (GST)', value: 'Asia/Dubai' },
  { label: 'UTC', value: 'UTC' },
]

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
  if (user.value) {
    Object.assign(form, {
      full_name: user.value.full_name || '',
      phone: user.value.phone || '',
      exotel_account_sid: user.value.exotel_account_sid || '',
      exotel_api_key: user.value.exotel_api_key || '',
      exotel_api_token: user.value.exotel_api_token || '',
      exotel_caller_id: user.value.exotel_caller_id || '',
      timezone: user.value.timezone || 'Asia/Kolkata',
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
