import api from '@/api/client'

export default {
  async list(page = 1, limit = 20, status = null) {
    const params = { page, limit }
    if (status) params.status_filter = status
    const res = await api.get('/campaigns', { params })
    return res.data
  },

  async get(id) {
    const res = await api.get(`/campaigns/${id}`)
    return res.data
  },

  async create(data) {
    const res = await api.post('/campaigns', data)
    return res.data
  },

  async update(id, data) {
    const res = await api.put(`/campaigns/${id}`, data)
    return res.data
  },

  async delete(id) {
    const res = await api.delete(`/campaigns/${id}`)
    return res.data
  },

  async start(id) {
    const res = await api.post(`/campaigns/${id}/start`)
    return res.data
  },

  async pause(id) {
    const res = await api.post(`/campaigns/${id}/pause`)
    return res.data
  },

  async resume(id) {
    const res = await api.post(`/campaigns/${id}/resume`)
    return res.data
  },

  async getCallLogs(id, page = 1, limit = 50, status = null) {
    const params = { page, limit }
    if (status) params.status_filter = status
    const res = await api.get(`/campaigns/${id}/call-logs`, { params })
    return res.data
  },
}
