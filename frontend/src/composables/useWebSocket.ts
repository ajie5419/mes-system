import { ref } from 'vue'
import axios from '../api'

export type WsStatus = 'connected' | 'reconnecting' | 'disconnected'

const status = ref<WsStatus>('disconnected')
let ws: WebSocket | null = null
let heartbeatTimer: ReturnType<typeof setInterval> | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let retryCount = 0
const maxRetries = 5
const retryDelays = [3000, 6000, 12000, 30000, 30000]
let messageHandler: ((data: any) => void) | null = null

function getToken(): string | null {
  return localStorage.getItem('token')
}

function getWsUrl(token: string): string {
  const base = axios.defaults.baseURL || ''
  const url = new URL(base + '/ws/notifications', window.location.origin)
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  url.searchParams.set('token', token)
  return url.toString()
}

export function useWebSocket() {
  function connect(onMessage?: (data: any) => void) {
    if (onMessage) messageHandler = onMessage
    const token = getToken()
    if (!token) return

    try {
      ws = new WebSocket(getWsUrl(token))
    } catch {
      status.value = 'disconnected'
      return
    }

    status.value = 'reconnecting'

    ws.onopen = () => {
      status.value = 'connected'
      retryCount = 0
      startHeartbeat()
    }

    ws.onmessage = (event) => {
      if (event.data === 'pong') return
      try {
        const data = JSON.parse(event.data)
        messageHandler?.(data)
      } catch { /* ignore */ }
    }

    ws.onclose = () => {
      stopHeartbeat()
      status.value = 'disconnected'
      scheduleReconnect()
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  function disconnect() {
    retryCount = maxRetries // prevent reconnect
    stopHeartbeat()
    clearTimeout(reconnectTimer)
    ws?.close()
    ws = null
    status.value = 'disconnected'
  }

  function scheduleReconnect() {
    if (retryCount >= maxRetries) return
    const delay = retryDelays[retryCount] || 30000
    retryCount++
    status.value = 'reconnecting'
    reconnectTimer = setTimeout(() => connect(), delay)
  }

  function startHeartbeat() {
    stopHeartbeat()
    heartbeatTimer = setInterval(() => {
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send('ping')
      }
    }, 30000)
  }

  function stopHeartbeat() {
    if (heartbeatTimer) {
      clearInterval(heartbeatTimer)
      heartbeatTimer = null
    }
  }

  return { status, connect, disconnect }
}
