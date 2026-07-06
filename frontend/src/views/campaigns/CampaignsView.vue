<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
        class="flex justify-between items-center"
      >
        <div>
          <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">Campaigns</h1>
          <p class="text-sm text-surface-500 mt-1">Manage your outbound calling campaigns</p>
        </div>
        <Button as="router-link" to="/campaigns/new" label="New Campaign">
          <template #icon><Plus :size="16" /></template>
        </Button>
      </motion.div>

      <SelectButton v-model="currentFilter" :options="filters" option-label="label" option-value="value" class="mb-2" />

      <!-- Loading -->
      <div v-if="loading" class="grid gap-4">
        <div v-for="i in 3" :key="i" class="card space-y-3">
          <div class="flex items-center justify-between">
            <Skeleton width="12rem" height="1.25rem" />
            <Skeleton width="5rem" height="2rem" />
          </div>
          <Skeleton height="0.5rem" borderRadius="999px" />
        </div>
      </div>

      <!-- Empty state -->
      <motion.div
        v-else-if="campaigns.length === 0"
        initial="{ opacity: 0, scale: 0.95 }"
        animate="{ opacity: 1, scale: 1 }"
        class="card text-center py-12"
      >
        <div class="w-16 h-16 bg-emerald-100 dark:bg-emerald-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Phone :size="32" class="text-emerald-600 dark:text-emerald-400" />
        </div>
        <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-2">No campaigns yet</h3>
        <p class="text-surface-500 mb-2">Create a campaign to start making automated calls.</p>
        <p class="text-surface-400 text-sm mb-6">You'll need at least one script and one contact list first.</p>
        <Button as="router-link" to="/campaigns/new" label="New Campaign">
          <template #icon><Plus :size="16" /></template>
        </Button>
      </motion.div>

      <!-- Campaigns list -->
      <div v-else class="space-y-3">
        <router-link
          v-for="(c, idx) in campaigns"
          :key="c.id"
          :to="`/campaigns/${c.id}`"
          class="card-hover block cursor-pointer"
        >
          <motion.div
            initial="{ opacity: 0, y: 10 }"
            animate="{ opacity: 1, y: 0 }"
            transition="{ duration: 0.2, delay: idx * 0.05 }"
          >
            <div class="flex items-center justify-between">
              <div>
                <div class="flex items-center gap-2">
                  <h3 class="font-semibold text-surface-900 dark:text-surface-0">{{ c.name }}</h3>
                  <StatusBadge :status="c.status" />
                </div>
                <div class="flex items-center gap-4 mt-1.5 text-sm text-surface-500">
                  <span class="flex items-center gap-1"><Users :size="14" /> {{ c.total_contacts }} contacts</span>
                  <span class="flex items-center gap-1"><Clock :size="14" /> {{ c.schedule_type }}</span>
                  <span v-if="c.scheduled_at" class="flex items-center gap-1"><Calendar :size="14" /> {{ new Date(c.scheduled_at).toLocaleString() }}</span>
                </div>
              </div>
              <div class="flex items-center gap-2" @click.prevent>
                <Button v-if="c.status === 'draft' || c.status === 'paused'" label="Start" size="small" severity="success" @click="handleStart(c.id)">
                  <template #icon><Play :size="14" /></template>
                </Button>
                <Button v-if="c.status === 'running'" label="Pause" size="small" severity="secondary" outlined @click="handlePause(c.id)">
                  <template #icon><Pause :size="14" /></template>
                </Button>
                <Button size="small" severity="danger" text @click="handleDelete(c)">
                  <template #icon><Trash2 :size="14" /></template>
                </Button>
              </div>
            </div>
            <div class="mt-3 bg-surface-100 dark:bg-surface-800 rounded-full h-2">
              <div class="bg-emerald-500 h-2 rounded-full transition-all duration-700" :style="{ width: progressPercent(c) + '%' }"></div>
            </div>
            <div class="flex justify-between mt-1.5 text-xs text-surface-400">
              <span>{{ c.completed_contacts }}/{{ c.total_contacts }} completed</span>
              <span>{{ c.successful_contacts }} successful, {{ c.failed_contacts }} failed</span>
            </div>
          </motion.div>
        </router-link>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { motion } from 'motion-v'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import AppLayout from '@/components/layout/AppLayout.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { useCampaignsStore } from '@/stores/campaigns'
import { Plus, Phone, Users, Clock, Calendar, Play, Pause, Trash2 } from '@lucide/vue'
import Button from 'primevue/button'
import SelectButton from 'primevue/selectbutton'
import Skeleton from 'primevue/skeleton'

const campaignsStore = useCampaignsStore()
const { campaigns, loading } = storeToRefs(campaignsStore)
const confirm = useConfirm()
const toast = useToast()

const currentFilter = ref('')
const filters = [
  { label: 'All', value: '' },
  { label: 'Draft', value: 'draft' },
  { label: 'Running', value: 'running' },
  { label: 'Paused', value: 'paused' },
  { label: 'Completed', value: 'completed' },
]

watch(currentFilter, () => campaignsStore.fetchCampaigns(currentFilter.value))
onMounted(() => campaignsStore.fetchCampaigns())

function progressPercent(c) {
  return c.total_contacts > 0 ? Math.round((c.completed_contacts / c.total_contacts) * 100) : 0
}

async function handleStart(id) {
  await campaignsStore.startCampaign(id)
  toast.add({ severity: 'success', summary: 'Campaign started', life: 3000 })
}

async function handlePause(id) {
  await campaignsStore.pauseCampaign(id)
  toast.add({ severity: 'success', summary: 'Campaign paused', life: 3000 })
}

function handleDelete(campaign) {
  confirm.require({
    message: `Delete "${campaign.name}"? This cannot be undone.`,
    header: 'Delete campaign',
    acceptProps: { severity: 'danger', label: 'Delete' },
    rejectProps: { severity: 'secondary', outlined: true, label: 'Cancel' },
    accept: async () => {
      await campaignsStore.deleteCampaign(campaign.id)
      toast.add({ severity: 'success', summary: 'Campaign deleted', life: 3000 })
    },
  })
}
</script>
