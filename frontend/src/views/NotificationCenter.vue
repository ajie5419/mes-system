<template>
  <div class="page-container">
    <div class="page-header">
      <h2>🔔 通知中心</h2>
      <div style="display:flex;gap:8px;">
        <el-button type="primary" size="small" @click="handleMarkAllRead">全部已读</el-button>
      </div>
    </div>

    <div style="display:flex;gap:8px;margin-bottom:16px;">
      <el-radio-group v-model="filter" @change="loadData">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="unread">未读</el-radio-button>
        <el-radio-button value="warning">警告</el-radio-button>
        <el-radio-button value="error">错误</el-radio-button>
        <el-radio-button value="success">成功</el-radio-button>
      </el-radio-group>
    </div>

    <div v-if="notifications.length === 0" style="text-align:center;padding:60px 0;color:#999;">
      <el-icon :size="48"><BellFilled /></el-icon>
      <p style="margin-top:12px;">暂无通知</p>
    </div>

    <div v-else class="notification-list">
      <div v-for="n in notifications" :key="n.id" :class="['notification-card', { unread: !n.is_read }]" @click="handleClick(n)">
        <div class="notification-icon">
          <el-icon :size="20" :color="typeColor(n.type)">
            <WarningFilled v-if="n.type === 'warning'" />
            <CircleCloseFilled v-else-if="n.type === 'error'" />
            <SuccessFilled v-else-if="n.type === 'success'" />
            <InfoFilled v-else />
          </el-icon>
        </div>
        <div class="notification-body">
          <div class="notification-title">{{ n.title }}</div>
          <div class="notification-content">{{ n.content }}</div>
          <div class="notification-time">{{ formatTime(n.created_at) }}</div>
        </div>
        <div class="notification-actions" @click.stop>
          <el-button v-if="!n.is_read" type="primary" text size="small" @click="handleRead(n)">已读</el-button>
          <el-popconfirm title="确认删除？" @confirm="handleDelete(n)">
            <template #reference><el-button type="danger" text size="small">删除</el-button></template>
          </el-popconfirm>
        </div>
      </div>
    </div>

    <div class="pagination-bar" v-if="total > pageSize">
      <el-pagination background layout="prev, pager, next" :total="total" :page-size="pageSize" :current-page="page" @current-change="page = $event; loadData()" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { BellFilled, WarningFilled, CircleCloseFilled, SuccessFilled, InfoFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useNotificationStore } from '../stores/notification'

const store = useNotificationStore()
const filter = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const notifications = ref<any[]>([])

function typeColor(type: string) {
  return { info: '#1890ff', warning: '#faad14', error: '#ff4d4f', success: '#52c41a' }[type] || '#1890ff'
}

function formatTime(t: string) {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  if (d.toDateString() === now.toDateString()) return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) + ' ' + d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

async function loadData() {
  const params: any = { page: page.value, page_size: pageSize }
  if (filter.value === 'unread') params.unread_only = true
  else if (filter.value) params.type = filter.value
  const { data } = await (await import('../api')).default.get('/notifications', { params })
  notifications.value = data.items
  total.value = data.total
}

async function handleRead(n: any) {
  await store.markRead(n.id)
  n.is_read = true
}

async function handleMarkAllRead() {
  await store.markAllRead()
  notifications.value.forEach(n => n.is_read = true)
  ElMessage.success('已全部标记为已读')
}

async function handleDelete(n: any) {
  await store.deleteNotification(n.id)
  notifications.value = notifications.value.filter(x => x.id !== n.id)
  total.value--
}

function handleClick(n: any) {
  if (!n.is_read) handleRead(n)
  if (n.related_resource_type === 'work_order' && n.related_resource_id) {
    // Emit navigate event handled by App.vue
    window.dispatchEvent(new CustomEvent('notification-navigate', { detail: { type: n.related_resource_type, id: n.related_resource_id } }))
  }
}

onMounted(loadData)
</script>

<style scoped>
.notification-list { display: flex; flex-direction: column; gap: 8px; }
.notification-card {
  display: flex; align-items: flex-start; gap: 12px; padding: 14px 16px;
  background: #fafafa; border-radius: 8px; cursor: pointer; transition: all .2s;
  border: 1px solid transparent;
}
.notification-card:hover { background: #f0f5ff; border-color: #d6e4ff; }
.notification-card.unread { background: #e6f7ff; border-color: #91d5ff; }
.notification-icon { margin-top: 2px; flex-shrink: 0; }
.notification-body { flex: 1; min-width: 0; }
.notification-title { font-size: 14px; font-weight: 500; color: #1a1a1a; margin-bottom: 4px; }
.notification-content { font-size: 13px; color: #666; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.notification-time { font-size: 12px; color: #999; margin-top: 4px; }
.notification-actions { flex-shrink: 0; display: flex; gap: 4px; }
</style>
