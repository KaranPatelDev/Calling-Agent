import api from '@/api/client'

export default {
  async getDashboard() {
    const res = await api.get('/reports/dashboard')
    return res.data
  },

  async getCampaignStats(campaignId) {
    const res = await api.get(`/reports/campaigns/${campaignId}/stats`)
    return res.data
  },

  async exportCallLogs(campaignId, format = 'csv') {
    const res = await api.get(`/reports/campaigns/${campaignId}/export`, {
      params: { format },
      responseType: 'blob',
    })
    return res.data
  },
}
