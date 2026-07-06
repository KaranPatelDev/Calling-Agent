import api from '@/api/client'

export default {
  async list(page = 1, limit = 20) {
    const res = await api.get('/scripts', { params: { page, limit } })
    return res.data
  },

  async get(id) {
    const res = await api.get(`/scripts/${id}`)
    return res.data
  },

  async create(data) {
    const res = await api.post('/scripts', data)
    return res.data
  },

  async update(id, data) {
    const res = await api.put(`/scripts/${id}`, data)
    return res.data
  },

  async delete(id) {
    await api.delete(`/scripts/${id}`)
  },

  async activate(id) {
    const res = await api.post(`/scripts/${id}/activate`)
    return res.data
  },

  async uploadAudio(id, file) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post(`/scripts/${id}/audio`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async removeAudio(id) {
    const res = await api.delete(`/scripts/${id}/audio`)
    return res.data
  },

  getAudioPreviewUrl(id) {
    return `${api.defaults.baseURL}/scripts/${id}/audio/preview`
  },
}
