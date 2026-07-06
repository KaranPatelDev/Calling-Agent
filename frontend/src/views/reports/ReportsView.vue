<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
      >
        <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">Reports</h1>
        <p class="text-sm text-surface-500 mt-1">Analytics and insights for your campaigns</p>
      </motion.div>

      <!-- Loading -->
      <div v-if="loading" class="space-y-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div v-for="i in 4" :key="i" class="card space-y-2">
            <Skeleton width="6rem" height="1rem" />
            <Skeleton width="4rem" height="2rem" />
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="card text-center py-12">
        <AlertCircle :size="48" class="mx-auto text-red-400 mb-4" />
        <h3 class="text-lg font-semibold text-surface-700 dark:text-surface-200 mb-2">Unable to load reports</h3>
        <p class="text-surface-500">{{ error }}</p>
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
            <p class="text-sm text-surface-500">{{ stat.label }}</p>
            <p class="text-2xl font-bold" :class="stat.valueClass">{{ stat.value }}</p>
          </motion.div>
        </div>

        <!-- Breakdown -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <motion.div
            initial="{ opacity: 0, y: 10 }"
            animate="{ opacity: 1, y: 0 }"
            transition="{ delay: 0.3 }"
            class="card flex flex-col items-center"
          >
            <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-4 self-start">Call Outcomes</h2>
            <Chart type="doughnut" :data="chartData" :options="chartOptions" class="w-full max-w-[220px]" />
          </motion.div>

          <motion.div
            initial="{ opacity: 0, y: 10 }"
            animate="{ opacity: 1, y: 0 }"
            transition="{ delay: 0.4 }"
            class="card"
          >
            <h2 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-6">Call Breakdown</h2>
            <div class="space-y-5">
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-surface-700 dark:text-surface-200">Successful</span>
                  <span class="text-sm font-semibold text-emerald-600 dark:text-emerald-400">{{ stats.successful_calls }}</span>
                </div>
                <div class="w-full bg-surface-100 dark:bg-surface-800 rounded-full h-3">
                  <div class="bg-emerald-500 h-3 rounded-full transition-all duration-1000" :style="{ width: successPercent + '%' }"></div>
                </div>
              </div>
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-surface-700 dark:text-surface-200">Failed</span>
                  <span class="text-sm font-semibold text-red-600 dark:text-red-400">{{ stats.failed_calls }}</span>
                </div>
                <div class="w-full bg-surface-100 dark:bg-surface-800 rounded-full h-3">
                  <div class="bg-red-500 h-3 rounded-full transition-all duration-1000" :style="{ width: failPercent + '%' }"></div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { motion } from 'motion-v'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useDashboardStore } from '@/stores/dashboard'
import { useThemeStore } from '@/stores/theme'
import { AlertCircle } from '@lucide/vue'
import Skeleton from 'primevue/skeleton'
import Chart from 'primevue/chart'

const dashboardStore = useDashboardStore()
const themeStore = useThemeStore()
const { stats, loading, error } = storeToRefs(dashboardStore)

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
    { label: 'Total Campaigns', value: stats.value.total_campaigns, valueClass: 'text-blue-600 dark:text-blue-400' },
    { label: 'Active Campaigns', value: stats.value.active_campaigns, valueClass: 'text-emerald-600 dark:text-emerald-400' },
    { label: 'Total Calls Made', value: stats.value.total_calls, valueClass: 'text-purple-600 dark:text-purple-400' },
    { label: 'Success Rate', value: stats.value.success_rate + '%', valueClass: stats.value.success_rate >= 50 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400' },
  ]
})

const chartData = computed(() => ({
  labels: ['Successful', 'Failed'],
  datasets: [
    {
      data: [stats.value?.successful_calls || 0, stats.value?.failed_calls || 0],
      backgroundColor: ['#10b981', '#ef4444'],
      hoverBackgroundColor: ['#059669', '#dc2626'],
      borderWidth: 0,
    },
  ],
}))

const chartOptions = computed(() => {
  const textColor = themeStore.isDark ? '#e2e8f0' : '#475569'
  return {
    plugins: {
      legend: {
        position: 'bottom',
        labels: { color: textColor, usePointStyle: true },
      },
    },
    cutout: '65%',
    maintainAspectRatio: true,
    responsive: true,
  }
})
</script>
