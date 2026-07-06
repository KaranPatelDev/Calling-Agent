import api from '@/api/client'

export default {
  async register(data) {
    const res = await api.post('/auth/register', data)
    return res.data
  },

  async login(email, password) {
    const res = await api.post('/auth/login', { email, password })
    return res.data
  },

  async refreshToken(refresh_token) {
    const res = await api.post('/auth/refresh', { refresh_token })
    return res.data
  },

  async getMe() {
    const res = await api.get('/auth/me')
    return res.data
  },

  async updateMe(data) {
    const res = await api.put('/auth/me', data)
    return res.data
  },
}
