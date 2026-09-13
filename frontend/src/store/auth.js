import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import client from '../api/client'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const unreadCount = ref(0)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => {
    if (!user.value) return false
    if (user.value.isAdmin) return true
    return Array.isArray(user.value.roles) && user.value.roles.includes('ADMIN')
  })
  const currentUsername = computed(() => user.value?.username || 'User')

  function setAuth(newToken, newUser) {
    token.value = newToken
    user.value = newUser
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
    if (newUser) {
      localStorage.setItem('user', JSON.stringify(newUser))
    } else {
      localStorage.removeItem('user')
    }
  }

  function clearAuth() {
    token.value = null
    user.value = null
    unreadCount.value = 0
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function login(email, password) {
    const res = await client.post('/auth/login', { email, password })
    if (res.data && res.data.token) {
      setAuth(res.data.token, res.data.user)
      fetchUnreadCount().catch(() => {})
    }
    return res.data
  }

  async function register(email, username, password) {
    const res = await client.post('/auth/register', { email, username, password })
    if (res.data && res.data.token) {
      setAuth(res.data.token, res.data.user)
      fetchUnreadCount().catch(() => {})
    }
    return res.data
  }

  async function fetchMe() {
    if (!token.value) return null
    try {
      const res = await client.get('/auth/me')
      user.value = res.data
      localStorage.setItem('user', JSON.stringify(res.data))
      return res.data
    } catch (err) {
      if (err.response?.status === 401) {
        clearAuth()
      }
      throw err
    }
  }

  async function fetchUnreadCount() {
    if (!token.value) return
    try {
      const res = await client.get('/notifications')
      unreadCount.value = res.data.unread_count || 0
    } catch (e) {}
  }

  async function logout() {
    try {
      await client.post('/auth/logout')
    } catch (e) {}
    clearAuth()
  }

  return {
    token,
    user,
    unreadCount,
    isAuthenticated,
    isAdmin,
    currentUsername,
    setAuth,
    clearAuth,
    login,
    register,
    fetchMe,
    fetchUnreadCount,
    logout
  }
})
