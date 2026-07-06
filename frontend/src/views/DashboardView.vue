<template>
  <AppLayout>
    <div class="space-y-6">
      <motion.div
        initial="{ opacity: 0, y: -10 }"
        animate="{ opacity: 1, y: 0 }"
        class="flex justify-between items-center"
      >
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p class="text-sm text-gray-500 mt-1">Welcome back, {{ authStore.user?.full_name || 'there' }}</p>
        </div>
        <button @click="refresh" class="btn-secondary text-sm flex items-center gap-2">
          <RefreshCw :size="16" :class="{ 'animate-spin': loading }" />
          Refresh
        </button>
      </motion.div>

      <!-- Loading skeleton -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div v-for="i in 4" :key="i" class="card">
          <div class="skeleton h-4 w-24 mb-3"></div>
          <div class="skeleton h-10 w-20"></div>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="card text-center py-12">
        <AlertCircle :size="48" class="mx-auto text-red-400 mb-4" />
        <h3 class="text-lg font-semibold text-gray-700 mb-2">Something went wrong</h3>
        <p class="text-gray-500 mb-4">{{ error }}</p>
        <button @click="refresh" class="btn-primary">Try Again</button>
      </div>

      <!-- Empty state -->
      <motion.div
        v-else-if="stats && stats.total_campaigns === 0"
        initial="{ opacity: 0, scale: 0.95 }"
        animate="{ opacity: 1, scale: 1 }"
        transition="{ duration: 0.4 }"
        class="card text-center py-12"
      >
        <div class="w-20 h-20 bg-gradient-to-br from-brand-100 to-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <Rocket :size="36" class="text-brand-600" />
        </div>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">Welcome to Calling Agent</h3>
        <p class="text-gray-500 mb-8 max-w-md mx-auto">Get started by creating your first script, contact list, and campaign.</p>
        <div class="flex flex-col sm:flex-row justify-center gap-3">
          <router-link to="/scripts" class="btn-primary flex items-center justify-center gap-2">
            <FileText :size="18" />
            1. Create Script
          </router-link>
          <router-link to="/contacts" class="btn-primary flex items-center justify-center gap-2">
            <Users :size="18" />
            2. Add Contacts
          </router-link>
          <router-link to="/campaigns/new" class="btn-success flex items-center justify-center gap-2">
            <Phone :size="18" />
            3. Start Campaign
          </router-link>
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
            <p class="text-sm text-gray-500">{{ stat.label }}</p>
            <div class="w-10 h-10 rounded-xl flex items-center justify-center" :class="stat.bgClass">
              <component :is="stat.icon" :size="20" :class="stat.iconClass" />
            </div>
          </div>
          <p class="text-3xl font-bold mt-2" :class="stat.valueClass">{{ stat.value }}</p>
        </motion.div>
      </div>

      <!-- Call breakdown -->
      <div v-if="stats && stats.total_campaigns > 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div
          initial="{ opacity: 0, y: 20 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ duration: 0.3, delay: 0.3 }"
          class="card"
        >
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Successful Calls</h3>
          <div class="flex items-end gap-3">
            <p class="text-4xl font-bold text-emerald-600">{{ stats.successful_calls }}</p>
            <div class="flex-1 bg-gray-100 rounded-full h-3 mb-2">
              <div class="bg-emerald-500 h-3 rounded-full transition-all duration-700" :style="{ width: successPercent + '%' }"></div>
            </div>
            <span class="text-sm text-gray-500 mb-2">{{ successPercent }}%</span>
          </div>
        </motion.div>

        <motion.div
          initial="{ opacity: 0, y: 20 }"
          animate="{ opacity: 1, y: 0 }"
          transition="{ duration: 0.3, delay: 0.4 }"
          class="card"
        >
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Failed Calls</h3>
          <div class="flex items-end gap-3">
            <p class="text-4xl font-bold text-red-600">{{ stats.failed_calls }}</p>
            <div class="flex-1 bg-gray-100 rounded-full h-3 mb-2">
              <div class="bg-red-500 h-3 rounded-full transition-all duration-700" :style="{ width: failPercent + '%' }"></div>
            </div>
            <span class="text-sm text-gray-500 mb-2">{{ failPercent }}%</span>
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
import { useAuthStore } from '@/stores/auth'
import { useDashboardStore } from '@/stores/dashboard'
import { RefreshCw, AlertCircle, Rocket, FileText, Users, Phone, BarChart3, PhoneCall, TrendingUp, Activity } from '@lucide/vue'

const authStore = useAuthStore()
const dashboardStore = useDashboardStore()
const { stats, loading, error } = dashboardStore

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
    { label: 'Total Campaigns', value: stats.value.total_campaigns, icon: BarChart3, bgClass: 'bg-blue-100', iconClass: 'text-blue-600', valueClass: 'text-blue-600' },
    { label: 'Active Campaigns', value: stats.value.active_campaigns, icon: Activity, bgClass: 'bg-emerald-100', iconClass: 'text-emerald-600', valueClass: 'text-emerald-600' },
    { label: 'Total Calls', value: stats.value.total_calls, icon: PhoneCall, bgClass: 'bg-purple-100', iconClass: 'text-purple-600', valueClass: 'text-purple-600' },
    { label: 'Success Rate', value: stats.value.success_rate + '%', icon: TrendingUp, bgClass: 'bg-amber-100', iconClass: 'text-amber-600', valueClass: stats.value.success_rate >= 50 ? 'text-emerald-600' : 'text-red-600' },
  ]
})
</script>
