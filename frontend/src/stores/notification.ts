import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '../api'
import { useWebSocket, type WsStatus } from '../composables/useWebSocket'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<any[]>([])
  const unreadCount = ref(0)
  const wsStatus = ref<WsStatus>('disconnected')
  let pollTimer: ReturnType<typeof setInterval> | null = null
  const { status, connect, disconnect } = useWebSocket()

  // Sync ws status reactively
  // We use a watch-like approach via callback
  const originalConnect = connect

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

  function handleWsMessage(data: any) {
    if (data.type === 'notification' || data.type === 'system' || data.type === 'alert') {
      fetchUnreadCount()
    }
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

  function connectWs() {
    originalConnect(handleWsMessage)
    // Sync status ref
    pollWsStatus()
  }

  function disconnectWs() {
    disconnect()
    stopPollWsStatus()
  }

  let wsStatusTimer: ReturnType<typeof setInterval> | null = null
  function pollWsStatus() {
    stopPollWsStatus()
    wsStatusTimer = setInterval(() => {
      wsStatus.value = status.value
    }, 500)
  }
  function stopPollWsStatus() {
    if (wsStatusTimer) {
      clearInterval(wsStatusTimer)
      wsStatusTimer = null
    }
  }

  return {
    notifications, unreadCount, wsStatus,
    fetchUnreadCount, fetchNotifications, markRead, markAllRead, deleteNotification,
    startPolling, stopPolling, connectWs, disconnectWs,
  }
})
