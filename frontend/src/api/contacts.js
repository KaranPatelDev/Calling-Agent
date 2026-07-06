import api from '@/api/client'

export default {
  async listLists(page = 1, limit = 20) {
    const res = await api.get('/contacts/lists', { params: { page, limit } })
    return res.data
  },

  async createList(data) {
    const res = await api.post('/contacts/lists', data)
    return res.data
  },

  async getList(id, page = 1, limit = 50) {
    const res = await api.get(`/contacts/lists/${id}`, { params: { page, limit } })
    return res.data
  },

  async deleteList(id) {
    await api.delete(`/contacts/lists/${id}`)
  },

  async addContact(listId, data) {
    const res = await api.post(`/contacts/lists/${listId}/contacts`, data)
    return res.data
  },

  async bulkUpload(listId, file) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post(`/contacts/upload`, formData, {
      params: { list_id: listId },
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },

  async validateUpload(file) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.get('/contacts/upload/validate', {
      params: { file: file.name },
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  },
}
