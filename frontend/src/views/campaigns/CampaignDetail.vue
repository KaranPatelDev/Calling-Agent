<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
        class="flex justify-between items-start"
      >
        <div>
          <router-link to="/campaigns" class="text-sm text-brand-600 hover:text-brand-700 flex items-center gap-1 mb-2">
            <ArrowLeft :size="14" />
            Back to Campaigns
          </router-link>
          <h1 class="text-2xl font-bold text-gray-900">{{ campaign?.name || 'Campaign' }}</h1>
        </div>
        <div class="flex gap-2">
          <button v-if="campaign?.status === 'draft' || campaign?.status === 'paused'" @click="handleStart" class="btn-success flex items-center gap-2">
            <Play :size="16" />
            Start
          </button>
          <button v-if="campaign?.status === 'running'" @click="handlePause" class="btn-secondary flex items-center gap-2">
            <Pause :size="16" />
            Pause
          </button>
          <button @click="handleExport" class="btn-secondary flex items-center gap-2">
            <Download :size="16" />
            Export CSV
          </button>
        </div>
      </motion.div>

      <!-- Loading -->
      <div v-if="!campaign" class="space-y-4">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div v-for="i in 4" :key="i" class="card text-center">
            <div class="skeleton h-4 w-16 mx-auto mb-2"></div>
            <div class="skeleton h-8 w-12 mx-auto"></div>
          </div>
        </div>
      </div>

      <template v-else>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <motion.div
            v-for="(stat, idx) in campaignStats"
            :key="stat.label"
            initial="{ opacity: 0, y: 10 }"
            animate="{ opacity: 1, y: 0 }"
            transition="{ delay: idx * 0.08 }"
            class="stat-card text-center"
          >
            <p class="text-sm text-gray-500">{{ stat.label }}</p>
            <p class="text-2xl font-bold" :class="stat.valueClass">{{ stat.value }}</p>
          </motion.div>
        </div>

        <motion.div
          initial="{ opacity: 0, y: 10 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ delay: 0.3 }"
          class="card"
        >
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Call Logs</h2>
          <div class="flex gap-2 mb-4">
            <button v-for="f in logFilters" :key="f.value" @click="currentLogFilter = f.value"
              class="px-3.5 py-1.5 rounded-full text-sm font-medium transition-all duration-200"
              :class="currentLogFilter === f.value ? 'bg-brand-600 text-white shadow-sm' : 'bg-white text-gray-600 border border-gray-200 hover:border-gray-300'">
              {{ f.label }}
            </button>
          </div>

          <div v-if="logsLoading" class="space-y-3">
            <div v-for="i in 5" :key="i" class="skeleton h-10 w-full"></div>
          </div>
          <div v-else-if="logs.length === 0" class="text-center py-8 text-gray-500">No call logs yet</div>
          <div v-else class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead class="table-header">
                <tr>
                  <th class="px-4 py-2">Contact</th>
                  <th class="px-4 py-2">Status</th>
                  <th class="px-4 py-2">Duration</th>
                  <th class="px-4 py-2">Retries</th>
                  <th class="px-4 py-2">Time</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50/50">
                  <td class="px-4 py-2.5 font-medium">{{ log.contact_id.substring(0, 8) }}...</td>
                  <td class="px-4 py-2.5">
                    <span class="badge" :class="logStatusClass(log.status)">{{ log.status }}</span>
                  </td>
                  <td class="px-4 py-2.5 text-gray-500">{{ log.duration_seconds }}s</td>
                  <td class="px-4 py-2.5 text-gray-500">{{ log.retry_count }}</td>
                  <td class="px-4 py-2.5 text-gray-500">{{ new Date(log.created_at).toLocaleString() }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </motion.div>
      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { motion } from 'motion-v'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useCampaignsStore } from '@/stores/campaigns'
import { useDashboardStore } from '@/stores/dashboard'
import { ArrowLeft, Play, Pause, Download } from '@lucide/vue'

const route = useRoute()
const campaignsStore = useCampaignsStore()
const dashboardStore = useDashboardStore()

const campaign = ref(null)
const logs = ref([])
const logsLoading = ref(false)
const currentLogFilter = ref('')

const logFilters = [
  { label: 'All', value: '' },
  { label: 'Completed', value: 'completed' },
  { label: 'Failed', value: 'failed' },
  { label: 'No Answer', value: 'no-answer' },
  { label: 'Busy', value: 'busy' },
]

const campaignStats = computed(() => {
  if (!campaign.value) return []
  const c = campaign.value
  return [
    { label: 'Status', value: c.status, valueClass: statusClass(c.status) },
    { label: 'Total', value: c.total_contacts, valueClass: 'text-gray-900' },
    { label: 'Successful', value: c.successful_contacts, valueClass: 'text-emerald-600' },
    { label: 'Failed', value: c.failed_contacts, valueClass: 'text-red-600' },
  ]
})

watch(currentLogFilter, () => loadLogs())

onMounted(async () => {
  campaign.value = await campaignsStore.getCampaign(route.params.id)
  await loadLogs()
})

async function loadLogs() {
  logsLoading.value = true
  try {
    const result = await campaignsStore.getCallLogs(route.params.id, currentLogFilter.value)
    logs.value = result.items
  } finally {
    logsLoading.value = false
  }
}

async function handleStart() {
  await campaignsStore.startCampaign(route.params.id)
  campaign.value = await campaignsStore.getCampaign(route.params.id)
}

async function handlePause() {
  await campaignsStore.pauseCampaign(route.params.id)
  campaign.value = await campaignsStore.getCampaign(route.params.id)
}

async function handleExport() {
  await dashboardStore.exportCallLogs(route.params.id)
}

function statusClass(status) {
  const map = { draft: 'text-gray-500', running: 'text-emerald-600', paused: 'text-amber-600', completed: 'text-purple-600' }
  return map[status] || 'text-gray-500'
}

function logStatusClass(status) {
  const map = {
    completed: 'badge-success',
    failed: 'badge-danger',
    'no-answer': 'badge-warning',
    busy: 'bg-orange-100 text-orange-800',
    dialing: 'badge-info',
  }
  return map[status] || 'badge-neutral'
}
</script>
