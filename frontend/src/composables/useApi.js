import api from '@/api/client'
import { ref } from 'vue'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  async function request(config) {
    loading.value = true
    error.value = null
    try {
      const response = await api(config)
      return response.data
    } catch (e) {
      error.value = e.response?.data?.detail || e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function get(url, params = {}) {
    return request({ method: 'GET', url, params })
  }

  async function post(url, data = {}) {
    return request({ method: 'POST', url, data })
  }

  async function put(url, data = {}) {
    return request({ method: 'PUT', url, data })
  }

  async function del(url) {
    return request({ method: 'DELETE', url })
  }

  return { loading, error, request, get, post, put, del }
}
