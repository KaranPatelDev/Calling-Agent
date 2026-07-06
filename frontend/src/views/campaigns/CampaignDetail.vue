<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
        class="flex justify-between items-start"
      >
        <div>
          <router-link to="/campaigns" class="text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1 mb-2">
            <ArrowLeft :size="14" />
            Back to Campaigns
          </router-link>
          <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">{{ campaign?.name || 'Campaign' }}</h1>
        </div>
        <div class="flex gap-2">
          <Button v-if="campaign?.status === 'draft' || campaign?.status === 'paused'" label="Start" severity="success" @click="handleStart">
            <template #icon><Play :size="16" /></template>
          </Button>
          <Button v-if="campaign?.status === 'running'" label="Pause" severity="secondary" outlined @click="handlePause">
            <template #icon><Pause :size="16" /></template>
          </Button>
          <Button label="Export CSV" severity="secondary" outlined @click="handleExport">
            <template #icon><Download :size="16" /></template>
          </Button>
        </div>
      </motion.div>

      <!-- Loading -->
      <div v-if="!campaign" class="space-y-4">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div v-for="i in 4" :key="i" class="card text-center space-y-2">
            <Skeleton width="4rem" height="1rem" class="mx-auto" />
            <Skeleton width="3rem" height="2rem" class="mx-auto" />
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
            <p class="text-sm text-surface-500">{{ stat.label }}</p>
            <p class="text-2xl font-bold" :class="stat.valueClass">{{ stat.value }}</p>
          </motion.div>
        </div>

        <motion.div
          initial="{ opacity: 0, y: 10 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ delay: 0.3 }"
          class="card"
        >
          <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-4">Call Logs</h2>
          <SelectButton v-model="currentLogFilter" :options="logFilters" option-label="label" option-value="value" class="mb-4" />

          <DataTable :value="logs" :loading="logsLoading" :rows="10" paginator responsive-layout="scroll">
            <template #empty>
              <div class="text-center py-8 text-surface-500">No call logs yet</div>
            </template>
            <Column header="Contact">
              <template #body="{ data }">{{ data.contact_id.substring(0, 8) }}...</template>
            </Column>
            <Column header="Status">
              <template #body="{ data }"><StatusBadge :status="data.status" /></template>
            </Column>
            <Column header="Duration">
              <template #body="{ data }">{{ data.duration_seconds }}s</template>
            </Column>
            <Column field="retry_count" header="Retries" />
            <Column header="Time">
              <template #body="{ data }">{{ new Date(data.created_at).toLocaleString() }}</template>
            </Column>
          </DataTable>
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
import StatusBadge from '@/components/common/StatusBadge.vue'
import { useCampaignsStore } from '@/stores/campaigns'
import { useDashboardStore } from '@/stores/dashboard'
import { ArrowLeft, Play, Pause, Download } from '@lucide/vue'
import Button from 'primevue/button'
import SelectButton from 'primevue/selectbutton'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Skeleton from 'primevue/skeleton'

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
    { label: 'Total', value: c.total_contacts, valueClass: 'text-surface-900 dark:text-surface-0' },
    { label: 'Successful', value: c.successful_contacts, valueClass: 'text-emerald-600 dark:text-emerald-400' },
    { label: 'Failed', value: c.failed_contacts, valueClass: 'text-red-600 dark:text-red-400' },
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
  const map = { draft: 'text-surface-500', running: 'text-emerald-600 dark:text-emerald-400', paused: 'text-amber-600 dark:text-amber-400', completed: 'text-purple-600 dark:text-purple-400' }
  return map[status] || 'text-surface-500'
}
</script>
