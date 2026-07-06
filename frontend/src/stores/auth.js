import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const initializing = ref(true)
  let readyResolve = null
  const ready = new Promise(resolve => { readyResolve = resolve })

  const isAuthenticated = computed(() => !!token.value)

  async function register(data) {
    const res = await api.post('/auth/register', data)
    return res.data
  }

  async function login(email, password) {
    const res = await api.post('/auth/login', { email, password })
    token.value = res.data.access_token
    refreshToken.value = res.data.refresh_token
    localStorage.setItem('token', token.value)
    localStorage.setItem('refreshToken', refreshToken.value)
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    await fetchUser()
  }

  async function fetchUser() {
    if (!token.value) {
      initializing.value = false
      readyResolve?.()
      return
    }
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    try {
      const res = await api.get('/auth/me')
      user.value = res.data
    } catch {
      logout()
    } finally {
      initializing.value = false
      readyResolve?.()
    }
  }

  async function updateProfile(data) {
    const res = await api.put('/auth/me', data)
    user.value = res.data
  }

  function logout() {
    user.value = null
    token.value = ''
    refreshToken.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    delete api.defaults.headers.common['Authorization']
  }

  if (token.value) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    fetchUser()
  } else {
    initializing.value = false
    readyResolve?.()
  }

  return { user, token, refreshToken, isAuthenticated, initializing, ready, register, login, fetchUser, updateProfile, logout }
})
