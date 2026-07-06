import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/client'

export const useCampaignsStore = defineStore('campaigns', () => {
  const campaigns = ref([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchCampaigns(status = null, page = 1, limit = 20) {
    loading.value = true
    try {
      const params = { page, limit }
      if (status) params.status_filter = status
      const res = await api.get('/campaigns', { params })
      campaigns.value = res.data.items
      total.value = res.data.total
    } finally {
      loading.value = false
    }
  }

  async function createCampaign(data) {
    const res = await api.post('/campaigns', data)
    campaigns.value.unshift(res.data)
    return res.data
  }

  async function getCampaign(id) {
    const res = await api.get(`/campaigns/${id}`)
    return res.data
  }

  async function updateCampaign(id, data) {
    const res = await api.put(`/campaigns/${id}`, data)
    const idx = campaigns.value.findIndex(c => c.id === id)
    if (idx !== -1) campaigns.value[idx] = res.data
    return res.data
  }

  async function deleteCampaign(id) {
    await api.delete(`/campaigns/${id}`)
    campaigns.value = campaigns.value.filter(c => c.id !== id)
  }

  async function startCampaign(id) {
    await api.post(`/campaigns/${id}/start`)
    const c = campaigns.value.find(c => c.id === id)
    if (c) c.status = 'running'
  }

  async function pauseCampaign(id) {
    await api.post(`/campaigns/${id}/pause`)
    const c = campaigns.value.find(c => c.id === id)
    if (c) c.status = 'paused'
  }

  async function resumeCampaign(id) {
    await api.post(`/campaigns/${id}/resume`)
    const c = campaigns.value.find(c => c.id === id)
    if (c) c.status = 'running'
  }

  async function getCallLogs(campaignId, status = null, page = 1, limit = 50) {
    const params = { page, limit }
    if (status) params.status_filter = status
    const res = await api.get(`/campaigns/${campaignId}/call-logs`, { params })
    return res.data
  }

  return { campaigns, total, loading, fetchCampaigns, createCampaign, getCampaign, updateCampaign, deleteCampaign, startCampaign, pauseCampaign, resumeCampaign, getCallLogs }
})
