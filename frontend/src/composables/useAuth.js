import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useAuth() {
  const authStore = useAuthStore()

  const user = computed(() => authStore.user)
  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const fullName = computed(() => authStore.user?.full_name || '')

  async function login(email, password) {
    return await authStore.login(email, password)
  }

  async function register(data) {
    return await authStore.register(data)
  }

  function logout() {
    authStore.logout()
  }

  async function fetchUser() {
    return await authStore.fetchUser()
  }

  return { user, isAuthenticated, fullName, login, register, logout, fetchUser }
}
