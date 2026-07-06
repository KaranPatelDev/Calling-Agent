import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/client'

export const useScriptsStore = defineStore('scripts', () => {
  const scripts = ref([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchScripts(page = 1, limit = 20) {
    loading.value = true
    try {
      const res = await api.get('/scripts', { params: { page, limit } })
      scripts.value = res.data.items
      total.value = res.data.total
    } finally {
      loading.value = false
    }
  }

  async function createScript(data) {
    const res = await api.post('/scripts', data)
    scripts.value.unshift(res.data)
    return res.data
  }

  async function updateScript(id, data) {
    const res = await api.put(`/scripts/${id}`, data)
    const idx = scripts.value.findIndex(s => s.id === id)
    if (idx !== -1) scripts.value[idx] = res.data
    return res.data
  }

  async function deleteScript(id) {
    await api.delete(`/scripts/${id}`)
    scripts.value = scripts.value.filter(s => s.id !== id)
  }

  async function activateScript(id) {
    await api.post(`/scripts/${id}/activate`)
    scripts.value.forEach(s => s.is_active = s.id === id)
  }

  async function uploadAudio(id, file) {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post(`/scripts/${id}/audio`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    const idx = scripts.value.findIndex(s => s.id === id)
    if (idx !== -1) scripts.value[idx] = res.data
    return res.data
  }

  async function removeAudio(id) {
    const res = await api.delete(`/scripts/${id}/audio`)
    const idx = scripts.value.findIndex(s => s.id === id)
    if (idx !== -1) scripts.value[idx] = res.data
    return res.data
  }

  async function uploadPreview(formData) {
    const res = await api.post('/scripts/upload-preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  }

  async function bulkImport(scriptsList) {
    const res = await api.post('/scripts/import', { scripts: scriptsList })
    for (const s of res.data) {
      scripts.value.unshift(s)
    }
    return res.data
  }

  return { scripts, total, loading, fetchScripts, createScript, updateScript, deleteScript, activateScript, uploadAudio, removeAudio, uploadPreview, bulkImport }
})
