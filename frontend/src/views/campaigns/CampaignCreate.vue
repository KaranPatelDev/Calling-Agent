<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
      >
        <h1 class="text-2xl font-bold text-gray-900">Create Campaign</h1>
        <p class="text-sm text-gray-500 mt-1">Set up a new outbound calling campaign</p>
      </motion.div>

      <motion.form
        @submit.prevent="handleCreate"
        initial="{ opacity: 0, y: 10 }"
        animate="{ opacity: 1, y: 0 }"
        transition="{ delay: 0.1 }"
        class="card space-y-6 max-w-2xl"
      >
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Campaign Name</label>
          <input v-model="form.name" type="text" required class="input-field" placeholder="e.g., June Outreach" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Script</label>
          <select v-model="form.script_id" required class="input-field">
            <option value="">Select a script</option>
            <option v-for="s in scripts" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Contact List</label>
          <select v-model="form.list_id" required class="input-field">
            <option value="">Select a contact list</option>
            <option v-for="l in lists" :key="l.id" :value="l.id">{{ l.name }} ({{ l.contact_count }} contacts)</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Schedule Type</label>
          <div class="flex gap-3">
            <label class="flex-1 flex items-center gap-2 p-3 rounded-xl border cursor-pointer transition-all" :class="form.schedule_type === 'immediate' ? 'border-brand-500 bg-brand-50' : 'border-gray-200 hover:border-gray-300'">
              <input type="radio" v-model="form.schedule_type" value="immediate" class="sr-only" />
              <Zap :size="18" :class="form.schedule_type === 'immediate' ? 'text-brand-600' : 'text-gray-400'" />
              <span class="text-sm font-medium" :class="form.schedule_type === 'immediate' ? 'text-brand-700' : 'text-gray-600'">Start Immediately</span>
            </label>
            <label class="flex-1 flex items-center gap-2 p-3 rounded-xl border cursor-pointer transition-all" :class="form.schedule_type === 'one_time' ? 'border-brand-500 bg-brand-50' : 'border-gray-200 hover:border-gray-300'">
              <input type="radio" v-model="form.schedule_type" value="one_time" class="sr-only" />
              <Clock :size="18" :class="form.schedule_type === 'one_time' ? 'text-brand-600' : 'text-gray-400'" />
              <span class="text-sm font-medium" :class="form.schedule_type === 'one_time' ? 'text-brand-700' : 'text-gray-600'">Schedule for Later</span>
            </label>
          </div>
        </div>

        <div v-if="form.schedule_type === 'one_time'">
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Scheduled Date/Time</label>
          <input v-model="form.scheduled_at" type="datetime-local" class="input-field" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Calling Hours Start</label>
            <input v-model.number="form.calling_hours_start" type="number" min="0" max="23" class="input-field" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Calling Hours End</label>
            <input v-model.number="form.calling_hours_end" type="number" min="0" max="23" class="input-field" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Max Concurrent Calls</label>
            <input v-model.number="form.max_concurrent_calls" type="number" min="1" max="20" class="input-field" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1.5">Retry Limit</label>
            <input v-model.number="form.retry_limit" type="number" min="0" max="5" class="input-field" />
          </div>
        </div>

        <transition name="fade">
          <div v-if="error" class="flex items-center gap-2 p-3 rounded-xl bg-red-50 border border-red-100">
            <AlertCircle :size="16" class="text-red-500 shrink-0" />
            <p class="text-sm text-red-600">{{ error }}</p>
          </div>
        </transition>

        <div class="flex justify-end gap-2 pt-2">
          <router-link to="/campaigns" class="btn-secondary">Cancel</router-link>
          <button type="submit" :disabled="submitting" class="btn-primary flex items-center gap-2">
            <Loader2 v-if="submitting" :size="16" class="animate-spin" />
            {{ submitting ? 'Creating...' : 'Create Campaign' }}
          </button>
        </div>
      </motion.form>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { motion } from 'motion-v'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useScriptsStore } from '@/stores/scripts'
import { useContactsStore } from '@/stores/contacts'
import { useCampaignsStore } from '@/stores/campaigns'
import { Zap, Clock, AlertCircle, Loader2 } from '@lucide/vue'

const router = useRouter()
const scriptsStore = useScriptsStore()
const contactsStore = useContactsStore()
const campaignsStore = useCampaignsStore()

const scripts = ref([])
const lists = ref([])
const submitting = ref(false)
const error = ref('')

const form = reactive({
  name: '',
  script_id: '',
  list_id: '',
  schedule_type: 'immediate',
  scheduled_at: '',
  calling_hours_start: 9,
  calling_hours_end: 21,
  max_concurrent_calls: 5,
  retry_limit: 3,
  retry_cooldown_minutes: 30,
})

onMounted(async () => {
  await scriptsStore.fetchScripts()
  await contactsStore.fetchLists()
  scripts.value = scriptsStore.scripts
  lists.value = contactsStore.lists
})

async function handleCreate() {
  submitting.value = true
  error.value = ''
  try {
    const payload = { ...form }
    if (payload.schedule_type === 'one_time' && payload.scheduled_at) {
      payload.scheduled_at = new Date(payload.scheduled_at).toISOString()
    }
    const campaign = await campaignsStore.createCampaign(payload)
    router.push(`/campaigns/${campaign.id}`)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to create campaign'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: all 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
