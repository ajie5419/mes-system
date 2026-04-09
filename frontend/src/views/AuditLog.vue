<template>
  <div class="page-container">
    <div class="page-header">
      <h2>操作日志</h2>
    </div>

    <!-- 筛选栏 -->
    <el-form :inline="true" class="filter-bar" @submit.prevent="fetchLogs">
      <el-form-item label="操作人">
        <el-select v-model="filters.user_id" clearable placeholder="全部" style="width:140px" @change="fetchLogs">
          <el-option v-for="u in userOptions" :key="u.id" :label="u.display_name" :value="u.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="操作类型">
        <el-select v-model="filters.action" clearable placeholder="全部" style="width:120px" @change="fetchLogs">
          <el-option v-for="a in actionOptions" :key="a" :label="a" :value="a" />
        </el-select>
      </el-form-item>
      <el-form-item label="资源类型">
        <el-select v-model="filters.resource_type" clearable placeholder="全部" style="width:140px" @change="fetchLogs">
          <el-option v-for="r in resourceOptions" :key="r" :label="r" :value="r" />
        </el-select>
      </el-form-item>
      <el-form-item label="日期范围">
        <el-date-picker v-model="filters.dateRange" type="daterange" range-separator="至"
          start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD"
          style="width:260px" @change="fetchLogs" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchLogs">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 表格 -->
    <el-table :data="logs" row-key="id" stripe v-loading="loading" style="width:100%">
      <el-table-column type="expand">
        <template #default="{ row }">
          <div style="padding:12px 24px">
            <template v-if="row.detail">
              <pre class="detail-json">{{ formatDetail(row.detail) }}</pre>
            </template>
            <template v-else>
              <span style="color:#999">无详情</span>
            </template>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="时间" prop="created_at" width="170" />
      <el-table-column label="操作人" prop="username" width="110" />
      <el-table-column label="操作类型" width="100">
        <template #default="{ row }">
          <el-tag :type="actionTagType(row.action)" size="small">{{ row.action }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="资源类型" prop="resource_type" width="120" />
      <el-table-column label="资源ID" prop="resource_id" width="90" />
      <el-table-column label="IP" prop="ip_address" width="140" />
    </el-table>

    <!-- 分页 -->
    <div class="pagination-bar">
      <el-pagination background layout="total, prev, pager, next, sizes"
        :total="total" :page-size="filters.page_size" :current-page="filters.page"
        :page-sizes="[20, 50, 100]"
        @current-change="onPageChange" @size-change="onSizeChange" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getAuditLogs, getUsers } from '../api'

const logs = ref<any[]>([])
const total = ref(0)
const loading = ref(false)
const userOptions = ref<any[]>([])

const actionOptions = ['create', 'update', 'delete', 'login', 'logout']
const resourceOptions = ['work_order', 'user', 'change', 'progress', 'supplier', 'drawing', 'quality_issue']

const filters = reactive({
  user_id: null as number | null,
  action: '',
  resource_type: '',
  dateRange: null as string[] | null,
  page: 1,
  page_size: 20,
})

function actionTagType(action: string): string {
  const map: Record<string, string> = { create: 'success', update: 'warning', delete: 'danger', login: 'info', logout: 'info' }
  return map[action] || ''
}

function formatDetail(detail: string): string {
  try {
    return JSON.stringify(JSON.parse(detail), null, 2)
  } catch {
    return detail
  }
}

async function fetchLogs() {
  loading.value = true
  try {
    const params: any = {
      page: filters.page,
      page_size: filters.page_size,
    }
    if (filters.user_id) params.user_id = filters.user_id
    if (filters.action) params.action = filters.action
    if (filters.resource_type) params.resource_type = filters.resource_type
    if (filters.dateRange?.length === 2) {
      params.start_date = filters.dateRange[0]
      params.end_date = filters.dateRange[1]
    }
    const data = await getAuditLogs(params)
    logs.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function onPageChange(p: number) { filters.page = p; fetchLogs() }
function onSizeChange(s: number) { filters.page_size = s; filters.page = 1; fetchLogs() }

function resetFilters() {
  filters.user_id = null
  filters.action = ''
  filters.resource_type = ''
  filters.dateRange = null
  filters.page = 1
  fetchLogs()
}

onMounted(async () => {
  try {
    const users = await getUsers()
    userOptions.value = users
  } catch { /* ignore */ }
  fetchLogs()
})
</script>

<style scoped>
.filter-bar { margin-bottom: 16px; }
.detail-json {
  background: #f5f5f5; border-radius: 6px; padding: 12px 16px;
  font-size: 12px; line-height: 1.6; max-height: 300px; overflow: auto;
  white-space: pre-wrap; word-break: break-all;
}
</style>
