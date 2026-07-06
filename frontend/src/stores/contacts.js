import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/client'

export const useContactsStore = defineStore('contacts', () => {
  const lists = ref([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchLists(page = 1, limit = 20) {
    loading.value = true
    try {
      const res = await api.get('/contacts/lists', { params: { page, limit } })
      lists.value = res.data.items
      total.value = res.data.total
    } finally {
      loading.value = false
    }
  }

  async function createList(data) {
    const res = await api.post('/contacts/lists', data)
    lists.value.unshift(res.data)
    return res.data
  }

  async function deleteList(id) {
    await api.delete(`/contacts/lists/${id}`)
    lists.value = lists.value.filter(l => l.id !== id)
  }

  async function getListContacts(listId, page = 1, limit = 50) {
    const res = await api.get(`/contacts/lists/${listId}`, { params: { page, limit } })
    return res.data
  }

  async function addContact(listId, data) {
    const res = await api.post(`/contacts/lists/${listId}/contacts`, data)
    const list = lists.value.find(l => l.id === listId)
    if (list) list.contact_count++
    return res.data
  }

  async function bulkUpload(listId, file) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/contacts/upload', formData, {
      params: { list_id: listId },
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    const list = lists.value.find(l => l.id === listId)
    if (list) list.contact_count += res.data.valid_rows
    return res.data
  }

  async function uploadPreview(formData) {
    const res = await api.post('/contacts/upload-preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  }

  async function bulkImportContacts(listId, contacts) {
    const res = await api.post(`/contacts/lists/${listId}/import`, contacts)
    const list = lists.value.find(l => l.id === listId)
    if (list) list.contact_count += res.data.valid_rows
    return res.data
  }

  return { lists, total, loading, fetchLists, createList, deleteList, getListContacts, addContact, bulkUpload, uploadPreview, bulkImportContacts }
})
