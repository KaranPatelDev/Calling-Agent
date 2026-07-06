<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
      >
        <h1 class="text-2xl font-bold text-gray-900">Reports</h1>
        <p class="text-sm text-gray-500 mt-1">Analytics and insights for your campaigns</p>
      </motion.div>

      <!-- Loading -->
      <div v-if="loading" class="space-y-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div v-for="i in 4" :key="i" class="card">
            <div class="skeleton h-4 w-24 mb-2"></div>
            <div class="skeleton h-8 w-16"></div>
          </div>
        </div>
      </div>

      <!-- Empty / Error -->
      <div v-else-if="error" class="card text-center py-12">
        <AlertCircle :size="48" class="mx-auto text-red-400 mb-4" />
        <h3 class="text-lg font-semibold text-gray-700 mb-2">Unable to load reports</h3>
        <p class="text-gray-500">{{ error }}</p>
      </div>

      <div v-else-if="stats" class="space-y-6">
        <!-- Stats -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <motion.div
            v-for="(stat, idx) in reportStats"
            :key="stat.label"
            initial="{ opacity: 0, y: 10 }"
            animate="{ opacity: 1, y: 0 }"
            transition="{ delay: idx * 0.08 }"
            class="stat-card"
          >
            <p class="text-sm text-gray-500">{{ stat.label }}</p>
            <p class="text-2xl font-bold" :class="stat.valueClass">{{ stat.value }}</p>
          </motion.div>
        </div>

        <!-- Breakdown -->
        <motion.div
          initial="{ opacity: 0, y: 10 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ delay: 0.3 }"
          class="card"
        >
          <h2 class="text-lg font-semibold text-gray-900 mb-6">Call Breakdown</h2>
          <div class="space-y-5">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Successful</span>
                <span class="text-sm font-semibold text-emerald-600">{{ stats.successful_calls }}</span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-3">
                <div class="bg-emerald-500 h-3 rounded-full transition-all duration-1000" :style="{ width: successPercent + '%' }"></div>
              </div>
            </div>
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700">Failed</span>
                <span class="text-sm font-semibold text-red-600">{{ stats.failed_calls }}</span>
              </div>
              <div class="w-full bg-gray-100 rounded-full h-3">
                <div class="bg-red-500 h-3 rounded-full transition-all duration-1000" :style="{ width: failPercent + '%' }"></div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { motion } from 'motion-v'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useDashboardStore } from '@/stores/dashboard'
import { AlertCircle } from '@lucide/vue'

const dashboardStore = useDashboardStore()
const { stats, loading, error } = dashboardStore

onMounted(() => dashboardStore.fetchDashboard())

const successPercent = computed(() => {
  if (!stats.value || stats.value.total_calls === 0) return 0
  return Math.round((stats.value.successful_calls / stats.value.total_calls) * 100)
})

const failPercent = computed(() => {
  if (!stats.value || stats.value.total_calls === 0) return 0
  return Math.round((stats.value.failed_calls / stats.value.total_calls) * 100)
})

const reportStats = computed(() => {
  if (!stats.value) return []
  return [
    { label: 'Total Campaigns', value: stats.value.total_campaigns, valueClass: 'text-blue-600' },
    { label: 'Active Campaigns', value: stats.value.active_campaigns, valueClass: 'text-emerald-600' },
    { label: 'Total Calls Made', value: stats.value.total_calls, valueClass: 'text-purple-600' },
    { label: 'Success Rate', value: stats.value.success_rate + '%', valueClass: stats.value.success_rate >= 50 ? 'text-emerald-600' : 'text-red-600' },
  ]
})
</script>
