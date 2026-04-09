import { client } from './api'

export const getWorkOrderPrintData = (woId: number) =>
  client.get(`/print/work-order/${woId}`).then(res => res.data)

export const getProgressReportPrintData = (woId: number) =>
  client.get(`/print/progress-report/${woId}`).then(res => res.data)
