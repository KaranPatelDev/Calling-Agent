import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/client'

export const useDashboardStore = defineStore('dashboard', () => {
  const stats = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchDashboard() {
    loading.value = true
    error.value = null
    try {
      const res = await api.get('/reports/dashboard')
      stats.value = res.data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Failed to load dashboard'
      stats.value = null
    } finally {
      loading.value = false
    }
  }

  async function getCampaignStats(campaignId) {
    const res = await api.get(`/reports/campaigns/${campaignId}/stats`)
    return res.data
  }

  async function exportCallLogs(campaignId, format = 'csv') {
    const res = await api.get(`/reports/campaigns/${campaignId}/export`, {
      params: { format },
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `call_logs_${campaignId}.${format}`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  }

  return { stats, loading, error, fetchDashboard, getCampaignStats, exportCallLogs }
})
