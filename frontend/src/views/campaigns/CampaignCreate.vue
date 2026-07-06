<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
      >
        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">Create Campaign</h1>
        <p class="text-sm text-surface-500 mt-1">Set up a new outbound calling campaign</p>
      </motion.div>

      <motion.form
        @submit.prevent="handleCreate"
        initial="{ opacity: 0, y: 10 }"
        animate="{ opacity: 1, y: 0 }"
        transition="{ delay: 0.1 }"
        class="card space-y-6 max-w-2xl"
      >
        <div>
          <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Campaign Name</label>
          <InputText v-model="form.name" required class="w-full" placeholder="e.g., June Outreach" />
        </div>

        <div>
          <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Script</label>
          <Select v-model="form.script_id" :options="scripts" option-label="name" option-value="id" placeholder="Select a script" required class="w-full" />
        </div>

        <div>
          <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Contact List</label>
          <Select v-model="form.list_id" :options="listOptions" option-label="label" option-value="value" placeholder="Select a contact list" required class="w-full" />
        </div>

        <div>
          <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Schedule Type</label>
          <div class="flex gap-3">
            <label class="flex-1 flex items-center gap-2 p-3 rounded-xl border cursor-pointer transition-all" :class="form.schedule_type === 'immediate' ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10' : 'border-surface-200 dark:border-surface-600 hover:border-surface-300'">
              <input type="radio" v-model="form.schedule_type" value="immediate" class="sr-only" />
              <Zap :size="18" :class="form.schedule_type === 'immediate' ? 'text-primary-600' : 'text-surface-400'" />
              <span class="text-sm font-medium" :class="form.schedule_type === 'immediate' ? 'text-primary-700 dark:text-primary-400' : 'text-surface-600 dark:text-surface-300'">Start Immediately</span>
            </label>
            <label class="flex-1 flex items-center gap-2 p-3 rounded-xl border cursor-pointer transition-all" :class="form.schedule_type === 'one_time' ? 'border-primary-500 bg-primary-50 dark:bg-primary-500/10' : 'border-surface-200 dark:border-surface-600 hover:border-surface-300'">
              <input type="radio" v-model="form.schedule_type" value="one_time" class="sr-only" />
              <Clock :size="18" :class="form.schedule_type === 'one_time' ? 'text-primary-600' : 'text-surface-400'" />
              <span class="text-sm font-medium" :class="form.schedule_type === 'one_time' ? 'text-primary-700 dark:text-primary-400' : 'text-surface-600 dark:text-surface-300'">Schedule for Later</span>
            </label>
          </div>
        </div>

        <div v-if="form.schedule_type === 'one_time'">
          <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Scheduled Date/Time</label>
          <DatePicker v-model="form.scheduled_at" show-time hour-format="24" class="w-full" input-class="w-full" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Calling Hours Start</label>
            <InputNumber v-model="form.calling_hours_start" :min="0" :max="23" class="w-full" input-class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Calling Hours End</label>
            <InputNumber v-model="form.calling_hours_end" :min="0" :max="23" class="w-full" input-class="w-full" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Max Concurrent Calls</label>
            <InputNumber v-model="form.max_concurrent_calls" :min="1" :max="20" class="w-full" input-class="w-full" />
          </div>
          <div>
            <label class="block text-sm font-medium text-surface-700 dark:text-surface-200 mb-1.5">Retry Limit</label>
            <InputNumber v-model="form.retry_limit" :min="0" :max="5" class="w-full" input-class="w-full" />
          </div>
        </div>

        <transition name="fade">
          <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>
        </transition>

        <div class="flex justify-end gap-2 pt-2">
          <Button as="router-link" to="/campaigns" label="Cancel" severity="secondary" text />
          <Button type="submit" :loading="submitting" :label="submitting ? 'Creating...' : 'Create Campaign'" />
        </div>
      </motion.form>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { motion } from 'motion-v'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useScriptsStore } from '@/stores/scripts'
import { useContactsStore } from '@/stores/contacts'
import { useCampaignsStore } from '@/stores/campaigns'
import { Zap, Clock } from '@lucide/vue'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import DatePicker from 'primevue/datepicker'
import Button from 'primevue/button'
import Message from 'primevue/message'

const router = useRouter()
const scriptsStore = useScriptsStore()
const contactsStore = useContactsStore()
const campaignsStore = useCampaignsStore()

const scripts = ref([])
const lists = ref([])
const submitting = ref(false)
const error = ref('')

const listOptions = computed(() => lists.value.map(l => ({ label: `${l.name} (${l.contact_count} contacts)`, value: l.id })))

const form = reactive({
  name: '',
  script_id: '',
  list_id: '',
  schedule_type: 'immediate',
  scheduled_at: null,
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
    } else {
      payload.scheduled_at = null
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
