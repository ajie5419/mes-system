import axios from 'axios'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 15000
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default client

// ── 工单与看板 ──
export const getSummary = () => client.get('/dashboard/summary').then(res => res.data)
export const getWorkOrders = (params: any) => client.get('/work-orders/', { params }).then(res => res.data)
export const createWorkOrder = (data: any) => client.post('/work-orders/', data).then(res => res.data)
export const getWorkOrder = (id: number) => client.get(`/work-orders/${id}`).then(res => res.data)
export const updateWorkOrder = (id: number, data: any) => client.put(`/work-orders/${id}`, data).then(res => res.data)
export const deleteWorkOrder = (id: number) => client.delete(`/work-orders/${id}`).then(res => res.data)
export const createMilestone = (woId: number, data: any) => client.post(`/work-orders/${woId}/milestones`, data).then(res => res.data)

// ── 数据大屏 ──
export const getBigscreenOverview = () => client.get('/bigscreen/overview').then(res => res.data)

// ── 变更与进度 ──
export const getChanges = () => client.get('/changes/').then(res => res.data)
export const confirmChange = (id: number, data: any) => client.post(`/changes/${id}/confirm`, data).then(res => res.data)
export const reportProgress = (data: any) => client.post('/progress/report', data).then(res => res.data)
export const createChange = (data: any) => client.post('/changes/', data).then(res => res.data)
export const getProgress = (woId: number) => client.get(`/progress/${woId}`).then(res => res.data)

// ── 组织架构 ──
export const getUsers = (department?: string) => client.get('/users/', { params: department ? { department } : {} }).then(res => res.data)
export const createUser = (data: any) => client.post('/users/', data).then(res => res.data)
export const updateUser = (id: number, data: any) => client.patch(`/users/${id}`, data).then(res => res.data)

// ── 扩展模块 ──
export const getQualityIssues = () => client.get('/extra/quality-issues').then(res => res.data)
export const createQualityIssue = (data: any) => client.post('/extra/quality-issues', data).then(res => res.data)
export const getSuppliers = () => client.get('/extra/suppliers').then(res => res.data)
export const createSupplier = (data: any) => client.post('/extra/suppliers', data).then(res => res.data)
export const updateSupplier = (id: number, data: any) => client.put(`/extra/suppliers/${id}`, data).then(res => res.data)
export const deleteSupplier = (id: number) => client.delete(`/extra/suppliers/${id}`).then(res => res.data)
export const getDrawings = () => client.get('/extra/drawings').then(res => res.data)
export const createDrawing = (data: any) => client.post('/extra/drawings', data).then(res => res.data)

// ── 文件上传 ──
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

// ── 权限 ──
export const getPermissions = () => client.get('/permissions/').then(res => res.data)
export const getRolePermissions = () => client.get('/permissions/roles').then(res => res.data)
export const updateRolePermissions = (role: string, codes: string[]) => client.put(`/permissions/roles/${role}`, { permission_codes: codes }).then(res => res.data)

// ── 系统管理 ──
export const getSystemConfigs = (group?: string) => client.get('/system-config/', { params: group ? { group } : {} }).then(res => res.data)
export const updateSystemConfigs = (configs: any[]) => client.put('/system-config/batch', configs).then(res => res.data)
export const getDepartments = () => client.get('/departments/').then(res => res.data)
export const getDepartmentsFlat = () => client.get('/departments/flat').then(res => res.data)
export const createDepartment = (data: any) => client.post('/departments/', data).then(res => res.data)
export const updateDepartment = (id: number, data: any) => client.put(`/departments/${id}`, data).then(res => res.data)
export const deleteDepartment = (id: number) => client.delete(`/departments/${id}`).then(res => res.data)
export const getTemplates = () => client.get('/templates/').then(res => res.data)
export const getTemplateDetail = (id: number) => client.get(`/templates/${id}`).then(res => res.data)

// ── 认证 ──
export const login = (data: any) => client.post('/auth/login', data).then(res => res.data)
export const register = (data: any) => client.post('/auth/register', data).then(res => res.data)

// ── 审计日志 ──
export const getGanttData = (woId?: number) => client.get('/work-orders/gantt-data', { params: woId ? { wo_id: woId } : {} }).then(res => res.data)
export const getAuditLogs = (params: any) => client.get('/audit/logs', { params }).then(res => res.data)
export const getAuditLog = (id: number) => client.get(`/audit/logs/${id}`).then(res => res.data)

// ── 通知 ──
export const getNotifications = (params: any) => client.get('/notifications/', { params }).then(res => res.data)
export const getUnreadCount = () => client.get('/notifications/unread-count').then(res => res.data)
export const markNotificationRead = (id: number) => client.put(`/notifications/${id}/read`).then(res => res.data)
export const markAllNotificationsRead = () => client.put('/notifications/read-all').then(res => res.data)
export const deleteNotification = (id: number) => client.delete(`/notifications/${id}`).then(res => res.data)

// ── Webhook ──
export const getWebhookConfigs = () => client.get('/webhook/config').then(res => res.data)
export const createWebhookConfig = (data: any) => client.post('/webhook/config', data).then(res => res.data)
export const updateWebhookConfig = (id: number, data: any) => client.put(`/webhook/config/${id}`, data).then(res => res.data)
export const deleteWebhookConfig = (id: number) => client.delete(`/webhook/config/${id}`).then(res => res.data)
export const testWebhook = (data: any) => client.post('/webhook/test', data).then(res => res.data)

// ── 打印 ──
export const getWorkOrderPrintData = (woId: number) => client.get(`/print/work-order/${woId}`).then(res => res.data)
export const getProgressReportPrintData = (woId: number) => client.get(`/print/progress-report/${woId}`).then(res => res.data)

// ── 任务看板 ──
export const getTaskBoardOverview = () => client.get('/task-board/departments').then(res => res.data)
export const getDepartmentTasks = (deptId: number, status?: string) => client.get(`/task-board/department/${deptId}`, { params: status ? { status } : {} }).then(res => res.data)
export const createTask = (data: any) => client.post('/task-board/tasks', data).then(res => res.data)
export const updateTask = (id: number, data: any) => client.put(`/task-board/tasks/${id}`, data).then(res => res.data)
export const deleteTask = (id: number) => client.delete(`/task-board/tasks/${id}`).then(res => res.data)
export const moveTask = (id: number, status: string) => client.put(`/task-board/tasks/${id}/move`, { status }).then(res => res.data)

// ── 审批流 ──
export const getApprovalFlows = () => client.get('/approvals/flows').then(res => res.data)
export const createApprovalFlow = (data: any) => client.post('/approvals/flows', data).then(res => res.data)
export const startApproval = (data: any) => client.post('/approvals/start', data).then(res => res.data)
export const getPendingApprovals = (userId: number) => client.get('/approvals/pending', { params: { user_id: userId } }).then(res => res.data)
export const getApprovalHistory = (woId: number) => client.get(`/approvals/history/${woId}`).then(res => res.data)
export const approveStep = (stepId: number, userId: number, comment?: string) => client.post(`/approvals/steps/${stepId}/approve`, { user_id: userId, comment }).then(res => res.data)
export const rejectStep = (stepId: number, userId: number, comment?: string) => client.post(`/approvals/steps/${stepId}/reject`, { user_id: userId, comment }).then(res => res.data)

// ── 异常管理 ──
export const getExceptions = (params: any) => client.get('/exceptions/', { params }).then(res => res.data)
export const getException = (id: number) => client.get(`/exceptions/${id}`).then(res => res.data)
export const createException = (data: any) => client.post('/exceptions/', data).then(res => res.data)
export const updateException = (id: number, data: any) => client.put(`/exceptions/${id}`, data).then(res => res.data)
export const escalateException = (id: number) => client.put(`/exceptions/${id}/escalate`).then(res => res.data)
export const resolveException = (id: number, data: any) => client.put(`/exceptions/${id}/resolve`, data).then(res => res.data)
export const getExceptionStats = () => client.get('/exceptions/stats').then(res => res.data)

// ── 工单协作 ──
export const getWorkOrderAssignees = (woId: number) => client.get(`/work-orders/${woId}/assignees`).then(res => res.data)
export const assignWorkOrderDept = (woId: number, data: any) => client.post(`/work-orders/${woId}/assignees`, data).then(res => res.data)

// ── 自动化规则 ──
export const getAutomationRules = () => client.get('/automation/rules').then(res => res.data)
export const createAutomationRule = (data: any) => client.post('/automation/rules', data).then(res => res.data)
export const updateAutomationRule = (id: number, data: any) => client.put(`/automation/rules/${id}`, data).then(res => res.data)
export const deleteAutomationRule = (id: number) => client.delete(`/automation/rules/${id}`).then(res => res.data)
export const toggleAutomationRule = (id: number) => client.put(`/automation/rules/${id}/toggle`).then(res => res.data)
export const getAutomationLogs = (params?: any) => client.get('/automation/execution-log', { params }).then(res => res.data)

// ── 评论系统 ──
export const getComments = (resourceType: string, resourceId: number) => client.get(`/comments/${resourceType}/${resourceId}`).then(res => res.data)
export const createComment = (data: any) => client.post('/comments/', data).then(res => res.data)
export const deleteComment = (id: number) => client.delete(`/comments/${id}`).then(res => res.data)

// ── 时间线 ──
export const getWorkOrderTimeline = (woId: number) => client.get(`/work-orders/${woId}/timeline`).then(res => res.data)

// ── 数据分析 ──
export const getAnalyticsKPI = () => client.get('/analytics/kpi').then(res => res.data)
export const getWOTrend = (params?: any) => client.get('/analytics/work-orders/trend', { params }).then(res => res.data)
export const getWOCycleTime = () => client.get('/analytics/work-orders/cycle-time').then(res => res.data)
export const getWOOnTimeRate = () => client.get('/analytics/work-orders/on-time-rate').then(res => res.data)
export const getWOOverdue = () => client.get('/analytics/work-orders/overdue').then(res => res.data)
export const getDeptWorkload = () => client.get('/analytics/department/workload').then(res => res.data)
export const getDeptEfficiency = () => client.get('/analytics/department/efficiency').then(res => res.data)
export const getExceptionTrend = (params?: any) => client.get('/analytics/exceptions/trend', { params }).then(res => res.data)
export const getExceptionResolution = () => client.get('/analytics/exceptions/resolution').then(res => res.data)
export const getExceptionByType = () => client.get('/analytics/exceptions/by-type').then(res => res.data)
export const getExceptionByDept = () => client.get('/analytics/exceptions/by-department').then(res => res.data)
export const getProgressStreak = (params?: any) => client.get('/analytics/progress/streak', { params }).then(res => res.data)
export const getMilestoneCompletion = () => client.get('/analytics/milestone/completion').then(res => res.data)
