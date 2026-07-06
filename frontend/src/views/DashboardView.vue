<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
        class="flex justify-between items-center"
      >
        <div>
          <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0">Dashboard</h1>
          <p class="text-sm text-surface-500 mt-1">Welcome back, {{ authStore.user?.full_name || 'there' }}</p>
        </div>
        <Button label="Refresh" severity="secondary" outlined size="small" @click="refresh">
          <template #icon>
            <RefreshCw :size="16" :class="{ 'animate-spin': loading }" />
          </template>
        </Button>
      </motion.div>

      <!-- Loading skeleton -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div v-for="i in 4" :key="i" class="card">
          <Skeleton height="1rem" width="6rem" class="mb-3" />
          <Skeleton height="2.5rem" width="5rem" />
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="card text-center py-12">
        <AlertCircle :size="48" class="mx-auto text-red-400 mb-4" />
        <h3 class="text-lg font-semibold text-surface-700 dark:text-surface-200 mb-2">Something went wrong</h3>
        <p class="text-surface-500 mb-4">{{ error }}</p>
        <Button label="Try Again" @click="refresh" />
      </div>

      <!-- Empty state -->
      <motion.div
        v-else-if="stats && stats.total_campaigns === 0"
        initial="{ opacity: 0, scale: 0.95 }"
        animate="{ opacity: 1, scale: 1 }"
        transition="{ duration: 0.4 }"
        class="card text-center py-12"
      >
        <div class="w-20 h-20 bg-gradient-to-br from-primary-100 to-purple-100 dark:from-primary-500/20 dark:to-purple-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <Rocket :size="36" class="text-primary-600 dark:text-primary-400" />
        </div>
        <h3 class="text-xl font-semibold text-surface-900 dark:text-surface-0 mb-2">Welcome to Calling Agent</h3>
        <p class="text-surface-500 mb-8 max-w-md mx-auto">Get started by creating your first script, contact list, and campaign.</p>
        <div class="flex flex-col sm:flex-row justify-center gap-3">
          <Button as="router-link" to="/scripts" label="1. Create Script">
            <template #icon><FileText :size="18" /></template>
          </Button>
          <Button as="router-link" to="/contacts" label="2. Add Contacts">
            <template #icon><Users :size="18" /></template>
          </Button>
          <Button as="router-link" to="/campaigns/new" label="3. Start Campaign" severity="success">
            <template #icon><Phone :size="18" /></template>
          </Button>
        </div>
      </motion.div>

      <!-- Stats grid -->
      <div v-else-if="stats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          v-for="(stat, idx) in statCards"
          :key="stat.label"
          initial="{ opacity: 0, y: 20 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ duration: 0.3, delay: idx * 0.08 }"
          class="stat-card"
        >
          <div class="flex items-center justify-between">
            <p class="text-sm text-surface-500">{{ stat.label }}</p>
            <div class="w-10 h-10 rounded-xl flex items-center justify-center" :class="stat.bgClass">
              <component :is="stat.icon" :size="20" :class="stat.iconClass" />
            </div>
          </div>
          <p class="text-3xl font-bold mt-2" :class="stat.valueClass">{{ stat.value }}</p>
        </motion.div>
      </div>

      <!-- Call outcome breakdown -->
      <div v-if="stats && stats.total_campaigns > 0" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div
          initial="{ opacity: 0, y: 20 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ duration: 0.3, delay: 0.3 }"
          class="card lg:col-span-1 flex flex-col items-center"
        >
          <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-4 self-start">Call Outcomes</h3>
          <Chart type="doughnut" :data="chartData" :options="chartOptions" class="w-full max-w-[220px]" />
        </motion.div>

        <motion.div
          initial="{ opacity: 0, y: 20 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ duration: 0.3, delay: 0.4 }"
          class="card"
        >
          <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-4">Successful Calls</h3>
          <div class="flex items-end gap-3">
            <p class="text-4xl font-bold text-emerald-600 dark:text-emerald-400">{{ stats.successful_calls }}</p>
            <div class="flex-1 bg-surface-100 dark:bg-surface-800 rounded-full h-3 mb-2">
              <div class="bg-emerald-500 h-3 rounded-full transition-all duration-700" :style="{ width: successPercent + '%' }"></div>
            </div>
            <span class="text-sm text-surface-500 mb-2">{{ successPercent }}%</span>
          </div>
        </motion.div>

        <motion.div
          initial="{ opacity: 0, y: 20 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ duration: 0.3, delay: 0.5 }"
          class="card"
        >
          <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-0 mb-4">Failed Calls</h3>
          <div class="flex items-end gap-3">
            <p class="text-4xl font-bold text-red-600 dark:text-red-400">{{ stats.failed_calls }}</p>
            <div class="flex-1 bg-surface-100 dark:bg-surface-800 rounded-full h-3 mb-2">
              <div class="bg-red-500 h-3 rounded-full transition-all duration-700" :style="{ width: failPercent + '%' }"></div>
            </div>
            <span class="text-sm text-surface-500 mb-2">{{ failPercent }}%</span>
          </div>
        </motion.div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { motion } from 'motion-v'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import { useThemeStore } from '@/stores/theme'
import { RefreshCw, AlertCircle, Rocket, FileText, Users, Phone, BarChart3, PhoneCall, TrendingUp, Activity } from '@lucide/vue'
import Button from 'primevue/button'
import Skeleton from 'primevue/skeleton'
import Chart from 'primevue/chart'

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const themeStore = useThemeStore()
const { stats, loading, error } = storeToRefs(dashboardStore)

function refresh() {
  dashboardStore.fetchDashboard()
}

onMounted(refresh)

const successPercent = computed(() => {
  if (!stats.value || stats.value.total_calls === 0) return 0
  return Math.round((stats.value.successful_calls / stats.value.total_calls) * 100)
})

const failPercent = computed(() => {
  if (!stats.value || stats.value.total_calls === 0) return 0
  return Math.round((stats.value.failed_calls / stats.value.total_calls) * 100)
})

const statCards = computed(() => {
  if (!stats.value) return []
  return [
    { label: 'Total Campaigns', value: stats.value.total_campaigns, icon: BarChart3, bgClass: 'bg-blue-100 dark:bg-blue-500/20', iconClass: 'text-blue-600 dark:text-blue-400', valueClass: 'text-blue-600 dark:text-blue-400' },
    { label: 'Active Campaigns', value: stats.value.active_campaigns, icon: Activity, bgClass: 'bg-emerald-100 dark:bg-emerald-500/20', iconClass: 'text-emerald-600 dark:text-emerald-400', valueClass: 'text-emerald-600 dark:text-emerald-400' },
    { label: 'Total Calls', value: stats.value.total_calls, icon: PhoneCall, bgClass: 'bg-purple-100 dark:bg-purple-500/20', iconClass: 'text-purple-600 dark:text-purple-400', valueClass: 'text-purple-600 dark:text-purple-400' },
    { label: 'Success Rate', value: stats.value.success_rate + '%', icon: TrendingUp, bgClass: 'bg-amber-100 dark:bg-amber-500/20', iconClass: 'text-amber-600 dark:text-amber-400', valueClass: stats.value.success_rate >= 50 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400' },
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
