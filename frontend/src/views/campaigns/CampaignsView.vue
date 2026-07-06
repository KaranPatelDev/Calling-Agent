<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
        class="flex justify-between items-center"
      >
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p class="text-sm text-gray-500 mt-1">Manage your outbound calling campaigns</p>
        </div>
        <router-link to="/campaigns/new" class="btn-primary text-sm flex items-center gap-2">
          <Plus :size="16" />
          New Campaign
        </router-link>
      </motion.div>

      <div class="flex gap-2 mb-2">
        <button v-for="f in filters" :key="f.value" @click="currentFilter = f.value"
          class="px-3.5 py-1.5 rounded-full text-sm font-medium transition-all duration-200"
          :class="currentFilter === f.value ? 'bg-brand-600 text-white shadow-sm' : 'bg-white text-gray-600 border border-gray-200 hover:border-gray-300'">
          {{ f.label }}
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="grid gap-4">
        <div v-for="i in 3" :key="i" class="card">
          <div class="flex items-center justify-between mb-4">
            <div class="skeleton h-5 w-48 mb-2"></div>
            <div class="skeleton h-8 w-20"></div>
          </div>
          <div class="skeleton h-2 w-full rounded-full"></div>
        </div>
      </div>

      <!-- Empty state -->
      <motion.div
        v-else-if="campaigns.length === 0"
        initial="{ opacity: 0, scale: 0.95 }"
        animate="{ opacity: 1, scale: 1 }"
        class="card text-center py-12"
      >
        <div class="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Phone :size="32" class="text-emerald-600" />
        </div>
        <h3 class="text-lg font-semibold text-gray-900 mb-2">No campaigns yet</h3>
        <p class="text-gray-500 mb-2">Create a campaign to start making automated calls.</p>
        <p class="text-gray-400 text-sm mb-6">You'll need at least one script and one contact list first.</p>
        <router-link to="/campaigns/new" class="btn-primary inline-flex items-center gap-2">
          <Plus :size="16" />
          New Campaign
        </router-link>
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
                  <h3 class="font-semibold text-gray-900">{{ c.name }}</h3>
                  <span :class="statusClass(c.status)" class="badge">{{ c.status }}</span>
                </div>
                <div class="flex items-center gap-4 mt-1.5 text-sm text-gray-500">
                  <span class="flex items-center gap-1"><Users :size="14" /> {{ c.total_contacts }} contacts</span>
                  <span class="flex items-center gap-1"><Clock :size="14" /> {{ c.schedule_type }}</span>
                  <span v-if="c.scheduled_at" class="flex items-center gap-1"><Calendar :size="14" /> {{ new Date(c.scheduled_at).toLocaleString() }}</span>
                </div>
              </div>
              <div class="flex items-center gap-2" @click.prevent>
                <button v-if="c.status === 'draft' || c.status === 'paused'" @click="handleStart(c.id)" class="btn-success text-xs px-3 py-1.5 flex items-center gap-1">
                  <Play :size="14" />
                  Start
                </button>
                <button v-if="c.status === 'running'" @click="handlePause(c.id)" class="btn-secondary text-xs px-3 py-1.5 flex items-center gap-1">
                  <Pause :size="14" />
                  Pause
                </button>
                <button @click="handleDelete(c.id)" class="btn-ghost text-xs px-2 py-1.5 text-red-500 hover:text-red-700 hover:bg-red-50">
                  <Trash2 :size="14" />
                </button>
              </div>
            </div>
            <div class="mt-3 bg-gray-100 rounded-full h-2">
              <div class="bg-emerald-500 h-2 rounded-full transition-all duration-700" :style="{ width: progressPercent(c) + '%' }"></div>
            </div>
            <div class="flex justify-between mt-1.5 text-xs text-gray-400">
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
import { motion } from 'motion-v'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useCampaignsStore } from '@/stores/campaigns'
import { Plus, Phone, Users, Clock, Calendar, Play, Pause, Trash2 } from '@lucide/vue'

const campaignsStore = useCampaignsStore()
const { campaigns, loading } = campaignsStore

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

function statusClass(status) {
  const classes = {
    draft: 'bg-gray-100 text-gray-700',
    scheduled: 'bg-blue-100 text-blue-700',
    running: 'bg-emerald-100 text-emerald-700',
    paused: 'bg-amber-100 text-amber-700',
    completed: 'bg-purple-100 text-purple-700',
    failed: 'bg-red-100 text-red-700',
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

async function handleStart(id) { await campaignsStore.startCampaign(id) }
async function handlePause(id) { await campaignsStore.pauseCampaign(id) }
async function handleDelete(id) {
  if (confirm('Delete this campaign?')) { await campaignsStore.deleteCampaign(id) }
}
</script>
