import { defineStore } from 'pinia'
import client from '../api'

interface User {
  id: number
  username: string
  display_name: string
  department: string
  role: string
  is_active: boolean
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    token: localStorage.getItem('access_token') || '',
    isLoggedIn: !!localStorage.getItem('access_token'),
  }),

  actions: {
    async login(username: string, password: string) {
      const { data } = await client.post('/auth/login', { username, password })
      this.token = data.access_token
      this.user = data.user
      this.isLoggedIn = true
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
    },

    async register(payload: { username: string; display_name: string; password: string; department: string; role: string }) {
      const { data } = await client.post('/auth/register', payload)
      this.token = data.access_token
      this.user = data.user
      this.isLoggedIn = true
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
    },

    logout() {
      this.token = ''
      this.user = null
      this.isLoggedIn = false
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    },

    async refreshAuth(): Promise<boolean> {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) return false
      try {
        const { data } = await client.post('/auth/refresh', { refresh_token: refreshToken })
        this.token = data.access_token
        localStorage.setItem('access_token', data.access_token)
        return true
      } catch {
        this.logout()
        return false
      }
    },

    async fetchMe() {
      const { data } = await client.get('/auth/me')
      this.user = data
      this.isLoggedIn = true
    },
  },
})
