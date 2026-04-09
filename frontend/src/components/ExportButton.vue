<template>
  <el-button :type="type" :icon="Download" :loading="loading" @click="handleExport">
    {{ label }}
  </el-button>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = withDefaults(defineProps<{
  exportType: 'work-orders' | 'work-order-detail' | 'progress' | 'audit-logs' | 'users'
  label?: string
  type?: string
  params?: Record<string, any>
}>(), {
  label: '导出 Excel',
  type: 'success',
  params: () => ({})
})

const loading = ref(false)

async function handleExport() {
  loading.value = true
  try {
    const res = await exportApi(props.exportType, props.params)
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    const disposition = res.headers['content-disposition'] || ''
    const match = disposition.match(/filename=(.+)/)
    link.href = url
    link.download = match ? decodeURIComponent(match[1]) : `export_${Date.now()}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '导出失败')
  } finally {
    loading.value = false
  }
}

import axios from 'axios'

function exportApi(type: string, params: Record<string, any>) {
  const token = localStorage.getItem('access_token')
  const urlMap: Record<string, string> = {
    'work-orders': '/api/v1/export/work-orders',
    'work-order-detail': `/api/v1/export/work-orders/${params.id}`,
    'progress': '/api/v1/export/progress',
    'audit-logs': '/api/v1/export/audit-logs',
    'users': '/api/v1/export/users',
  }
  const url = urlMap[type]
  if (!url) throw new Error('未知的导出类型')
  const { id, ...queryParams } = params as any
  return axios.get(url, {
    params: Object.keys(queryParams).length ? queryParams : undefined,
    responseType: 'blob',
    headers: { Authorization: token ? `Bearer ${token}` : '' },
  })
}
</script>
