import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 10000
})

// 请求拦截器：自动附加 token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：401 时尝试刷新 token
let isRefreshing = false
let pendingRequests: Array<(token: string) => void> = []

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/auth/')) {
      if (isRefreshing) {
        return new Promise((resolve) => {
          pendingRequests.push((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(client(originalRequest))
          })
        })
      }
      originalRequest._retry = true
      isRefreshing = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) {
        window.location.hash = '#/login'
        return Promise.reject(error)
      }
      try {
        const { data } = await axios.post('/api/v1/auth/refresh', { refresh_token: refreshToken })
        const newToken = data.access_token
        localStorage.setItem('access_token', newToken)
        pendingRequests.forEach((cb) => cb(newToken))
        pendingRequests = []
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return client(originalRequest)
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.hash = '#/login'
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }
    return Promise.reject(error)
  }
)

// 工单与看板
export const getSummary = () => client.get('/dashboard/summary').then(res => res.data)
export const getWorkOrders = (params: any) => client.get('/work-orders/', { params }).then(res => res.data)
export const createWorkOrder = (data: any) => client.post('/work-orders/', data).then(res => res.data)
export const getWorkOrder = (id: number) => client.get(`/work-orders/${id}`).then(res => res.data)
export const updateWorkOrder = (id: number, data: any) => client.put(`/work-orders/${id}`, data).then(res => res.data)
export const deleteWorkOrder = (id: number) => client.delete(`/work-orders/${id}`).then(res => res.data)

// 变更与进度
export const getChanges = () => client.get('/changes/').then(res => res.data)
export const confirmChange = (id: number, data: any) => client.post(`/changes/${id}/confirm`, data).then(res => res.data)
export const reportProgress = (data: any) => client.post('/progress/report', data).then(res => res.data)
export const createChange = (data: any) => client.post('/changes/', data).then(res => res.data)
export const getProgress = (woId: number) => client.get(`/progress/${woId}`).then(res => res.data)

// 组织架构
export const getUsers = (department?: string) => client.get('/users/', { params: department ? { department } : {} }).then(res => res.data)
export const createUser = (data: any) => client.post('/users/', data).then(res => res.data)
export const updateUser = (id: number, data: any) => client.patch(`/users/${id}`, data).then(res => res.data)

// 扩展模块：质量、技术、采购
export const getQualityIssues = () => client.get('/extra/quality-issues').then(res => res.data)
export const createQualityIssue = (data: any) => client.post('/extra/quality-issues', data).then(res => res.data)
export const getSuppliers = () => client.get('/extra/suppliers').then(res => res.data)
export const createSupplier = (data: any) => client.post('/extra/suppliers', data).then(res => res.data)
export const updateSupplier = (id: number, data: any) => client.put(`/extra/suppliers/${id}`, data).then(res => res.data)
export const deleteSupplier = (id: number) => client.delete(`/extra/suppliers/${id}`).then(res => res.data)
export const getDrawings = () => client.get('/extra/drawings').then(res => res.data)
export const createDrawing = (data: any) => client.post('/extra/drawings', data).then(res => res.data)

// 文件上传
export const uploadFile = (file: File, directory?: string) => {
  const formData = new FormData()
  formData.append('file', file)
  if (directory) formData.append('directory', directory)
  return client.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(res => res.data)
}
export const createDrawingWithFile = (data: { wo_id: number; version: string; file?: File }) => {
  const formData = new FormData()
  formData.append('wo_id', String(data.wo_id))
  formData.append('version', data.version)
  if (data.file) formData.append('file', data.file)
  return client.post('/extra/drawings', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(res => res.data)
}
export const deleteUploadedFile = (file_path: string) => client.delete('/upload', { data: { file_path } }).then(res => res.data)

// 权限
export const getPermissions = () => client.get('/permissions/').then(res => res.data)
export const getRolePermissions = () => client.get('/permissions/roles').then(res => res.data)
export const updateRolePermissions = (role: string, codes: string[]) => client.put(`/permissions/roles/${role}`, { permission_codes: codes }).then(res => res.data)

// 认证
export const login = (data: any) => client.post('/auth/login', data).then(res => res.data)
export const register = (data: any) => client.post('/auth/register', data).then(res => res.data)

// 审计日志
export const getGanttData = (woId?: number) => client.get('/work-orders/gantt-data', { params: woId ? { wo_id: woId } : {} }).then(res => res.data)

export const getAuditLogs = (params: any) => client.get('/audit/logs', { params }).then(res => res.data)
export const getAuditLog = (id: number) => client.get(`/audit/logs/${id}`).then(res => res.data)

// 通知
export const getNotifications = (params: any) => client.get('/notifications/', { params }).then(res => res.data)
export const getUnreadCount = () => client.get('/notifications/unread-count').then(res => res.data)
export const markNotificationRead = (id: number) => client.put(`/notifications/${id}/read`).then(res => res.data)
export const markAllNotificationsRead = () => client.put('/notifications/read-all').then(res => res.data)
export const deleteNotification = (id: number) => client.delete(`/notifications/${id}`).then(res => res.data)

// Webhook
export const getWebhookConfigs = () => client.get('/webhook/config').then(res => res.data)
export const createWebhookConfig = (data: any) => client.post('/webhook/config', data).then(res => res.data)
export const updateWebhookConfig = (id: number, data: any) => client.put(`/webhook/config/${id}`, data).then(res => res.data)
export const deleteWebhookConfig = (id: number) => client.delete(`/webhook/config/${id}`).then(res => res.data)
export const testWebhook = (data: any) => client.post('/webhook/test', data).then(res => res.data)

// 打印
export const getWorkOrderPrintData = (woId: number) => client.get(`/print/work-order/${woId}`).then(res => res.data)
export const getProgressReportPrintData = (woId: number) => client.get(`/print/progress-report/${woId}`).then(res => res.data)

export default client
