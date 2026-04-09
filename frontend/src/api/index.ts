import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 5000
})

// 工单与看板
export const getSummary = () => client.get('/dashboard/summary').then(res => res.data)
export const getWorkOrders = (params: any) => client.get('/work-orders/', { params }).then(res => res.data)
export const createWorkOrder = (data: any) => client.post('/work-orders/', data).then(res => res.data)

// 变更与进度
export const getChanges = () => client.get('/changes/').then(res => res.data)
export const confirmChange = (id: number, data: any) => client.post(`/changes/${id}/confirm`, data).then(res => res.data)
export const reportProgress = (data: any) => client.post('/progress/report', data).then(res => res.data)

// 组织架构
export const getUsers = () => client.get('/users/').then(res => res.data)

// 扩展模块：质量、技术、采购
export const getQualityIssues = () => client.get('/extra/quality-issues').then(res => res.data)
export const createQualityIssue = (data: any) => client.post('/extra/quality-issues', data).then(res => res.data)
export const getSuppliers = () => client.get('/extra/suppliers').then(res => res.data)
export const getDrawings = () => client.get('/extra/drawings').then(res => res.data)

export default client
