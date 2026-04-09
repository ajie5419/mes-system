import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '../api'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<any[]>([])
  const unreadCount = ref(0)
  let pollTimer: ReturnType<typeof setInterval> | null = null

  async function fetchUnreadCount() {
    try {
      const { data } = await axios.get('/notifications/unread-count')
      unreadCount.value = data.count
    } catch { /* ignore */ }
  }

  async function fetchNotifications(params: any = {}) {
    const { data } = await axios.get('/notifications', { params })
    notifications.value = data.items
    return data
  }

  async function markRead(id: number) {
    await axios.put(`/notifications/${id}/read`)
    await fetchUnreadCount()
  }

  async function markAllRead() {
    await axios.put('/notifications/read-all')
    unreadCount.value = 0
  }

  async function deleteNotification(id: number) {
    await axios.delete(`/notifications/${id}`)
    await fetchUnreadCount()
  }

  function startPolling() {
    if (pollTimer) return
    fetchUnreadCount()
    pollTimer = setInterval(fetchUnreadCount, 30000)
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  return { notifications, unreadCount, fetchUnreadCount, fetchNotifications, markRead, markAllRead, deleteNotification, startPolling, stopPolling }
})
