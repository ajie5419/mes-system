<template>
  <Login v-if="!auth.isLoggedIn" @success="onLoginSuccess" />
  <div v-else class="mes-layout">
    <aside class="mes-sidebar">
      <div class="mes-logo">
        <el-icon class="logo-icon"><Odometer /></el-icon>
        <span class="logo-text">MES 智造系统</span>
      </div>

      <div class="mes-menu-wrapper">
        <el-menu default-active="dashboard" background-color="#001529" text-color="#ffffffa6" active-text-color="#ffffff" @select="handleMenuSelect">
          <el-menu-item index="dashboard" v-if="permStore.hasPermission('dashboard:read')"><el-icon><Monitor /></el-icon>质量看板</el-menu-item>
          <el-menu-item index="work-orders" v-if="permStore.hasPermission('work_orders:read')"><el-icon><Memo /></el-icon>工单府库</el-menu-item>
          <el-menu-item index="drawings" v-if="permStore.hasPermission('extra:read')"><el-icon><EditPen /></el-icon>图纸中心</el-menu-item>
          <el-menu-item index="suppliers" v-if="permStore.hasPermission('extra:read')"><el-icon><ShoppingCart /></el-icon>供应商</el-menu-item>
          <el-menu-item index="quality-issues" v-if="permStore.hasPermission('extra:read')"><el-icon><Checked /></el-icon>不合格品项</el-menu-item>
          <el-menu-item index="users" v-if="permStore.hasPermission('users:read')"><el-icon><User /></el-icon>吏部名册</el-menu-item>
          <el-menu-item index="permissions" v-if="auth.user?.role === 'Admin'"><el-icon><Lock /></el-icon>权限管理</el-menu-item>
          <el-menu-item index="gantt" v-if="permStore.hasPermission('work_orders:read')"><el-icon><DataLine /></el-icon>排程甘特图</el-menu-item>
          <el-menu-item index="audit-logs" v-if="permStore.hasPermission('audit:read')"><el-icon><Document /></el-icon>操作日志</el-menu-item>
          <el-menu-item index="notifications"><el-icon><Bell /></el-icon>通知中心</el-menu-item>
        </el-menu>
      </div>

      <div class="mes-user-panel">
        <div class="user-card">
          <el-avatar :size="32">{{ auth.user?.display_name?.[0] || 'U' }}</el-avatar>
          <div class="user-info"><div class="user-name">{{ auth.user?.display_name || '未知' }}</div><div class="user-role">{{ auth.user?.role || '' }}</div></div>
        </div>
        <el-button type="danger" text size="small" @click="auth.logout()" style="margin-left:auto;color:rgba(255,255,255,.45)">退出</el-button>
      </div>
    </aside>

    <section class="mes-main">
      <header class="mes-header">
        <el-breadcrumb separator="/"><el-breadcrumb-item>MES</el-breadcrumb-item><el-breadcrumb-item>{{ activeTabName }}</el-breadcrumb-item></el-breadcrumb>
        <div class="header-right">
          <el-badge :value="notifStore.unreadCount" :hidden="notifStore.unreadCount === 0" :max="99">
            <el-popover trigger="click" :width="360" v-model:visible="notifDropdown" @show="loadRecentNotifs">
              <template #reference>
                <el-button :icon="Bell" circle size="small" />
              </template>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="font-weight:600;">通知</span>
                <el-button type="primary" link size="small" @click="notifDropdown=false;handleMenuSelect('notifications')">查看全部</el-button>
              </div>
              <div v-if="recentNotifs.length === 0" style="text-align:center;color:#999;padding:20px 0;">暂无通知</div>
              <div v-for="n in recentNotifs" :key="n.id" style="padding:8px 0;border-bottom:1px solid #f0f0f0;cursor:pointer;" @click="notifDropdown=false;handleNotifClick(n)">
                <div style="font-size:13px;font-weight:500;color:#333;">{{ n.title }}</div>
                <div style="font-size:12px;color:#999;margin-top:2px;">{{ n.content?.substring(0, 40) }}{{ n.content?.length > 40 ? '...' : '' }}</div>
              </div>
            </el-popover>
          </el-badge>
          <el-input placeholder="搜索 (Ctrl+K)" class="search-input" prefix-icon="Search" />
        </div>
      </header>

      <nav class="mes-tabs">
        <div v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id" :class="['mes-tab-item', activeTab === tab.id ? 'active' : '']">
          {{ tab.name }} <el-icon v-if="tab.closeable" @click.stop="closeTab(tab.id)"><Close /></el-icon>
        </div>
      </nav>

      <main class="mes-content">
        <transition name="el-fade-in" mode="out-in">
          <component :is="currentView" :key="activeTab" @navigate="handleNavigate" :wo-id="currentWoId" />
        </transition>
      </main>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineAsyncComponent, markRaw, onMounted } from 'vue'
import { Monitor, Memo, User, Odometer, Search, Close, EditPen, ShoppingCart, Checked, Lock, Document, DataLine, Bell } from '@element-plus/icons-vue'
import { useAuthStore } from './stores/auth'
import { usePermissionStore } from './stores/permission'
import { useNotificationStore } from './stores/notification'
import Login from './views/Login.vue'

const auth = useAuthStore()
const permStore = usePermissionStore()
const notifStore = useNotificationStore()
const notifDropdown = ref(false)
const recentNotifs = ref<any[]>([])

onMounted(async () => {
  if (auth.isLoggedIn) {
    try { await auth.fetchMe() } catch { auth.logout() }
    if (auth.user?.role) {
      await permStore.loadForRole(auth.user.role)
    }
    notifStore.startPolling()
  }
})

// Listen for notification navigation
window.addEventListener('notification-navigate', ((e: any) => {
  if (e.detail.type === 'work_order') {
    handleNavigate({ id: 'work-order-detail', name: '工单详情', woId: e.detail.id })
  }
}) as EventListener)

function onLoginSuccess() { /* isLoggedIn is reactive, template auto-switches */ }

const Dashboard = markRaw(defineAsyncComponent(() => import('./views/Dashboard.vue')))
const WorkOrderList = markRaw(defineAsyncComponent(() => import('./views/WorkOrderList.vue')))
const UserList = markRaw(defineAsyncComponent(() => import('./views/UserList.vue')))
const QualityIssueList = markRaw(defineAsyncComponent(() => import('./views/QualityIssueList.vue')))
const DrawingList = markRaw(defineAsyncComponent(() => import('./views/DrawingList.vue')))
const SupplierList = markRaw(defineAsyncComponent(() => import('./views/SupplierList.vue')))
const WorkOrderDetail = markRaw(defineAsyncComponent(() => import('./views/WorkOrderDetail.vue')))
const PermissionManage = markRaw(defineAsyncComponent(() => import('./views/PermissionManage.vue')))
const AuditLogView = markRaw(defineAsyncComponent(() => import('./views/AuditLog.vue')))
const GanttView = markRaw(defineAsyncComponent(() => import('./views/GanttView.vue')))
const NotificationCenter = markRaw(defineAsyncComponent(() => import('./views/NotificationCenter.vue')))

const activeTab = ref('dashboard')
const tabs = ref([{ id: 'dashboard', name: '质量看板', closeable: false }])

const currentView = computed(() => {
  const map: any = {
    'dashboard': Dashboard,
    'work-orders': WorkOrderList,
    'users': UserList,
    'quality-issues': QualityIssueList,
    'drawings': DrawingList,
    'suppliers': SupplierList,
    'work-order-detail': WorkOrderDetail,
    'permissions': PermissionManage,
    'audit-logs': AuditLogView,
    'gantt': GanttView,
    'notifications': NotificationCenter,
  }
  return map[activeTab.value] || Dashboard
})

const currentWoId = ref<number | undefined>(undefined)

const activeTabName = computed(() => tabs.value.find(t => t.id === activeTab.value)?.name || '')

const handleMenuSelect = (index: string) => {
  const existingTab = tabs.value.find(t => t.id === index)
  if (!existingTab) {
    const names: any = {
      'dashboard': '质量看板', 'work-orders': '工单府库', 'users': '吏部名册',
      'quality-issues': '不合格品项', 'drawings': '图纸中心', 'suppliers': '供应商',
      'permissions': '权限管理',
      'audit-logs': '操作日志',
      'gantt': '排程甘特图',
      'notifications': '通知中心',
    }
    tabs.value.push({ id: index, name: names[index] || index, closeable: true })
  }
  activeTab.value = index
}

const handleNavigate = (payload: { id: string; name: string; woId?: number }) => {
  const tabKey = payload.id
  const existing = tabs.value.find(t => t.id === tabKey)
  if (!existing) {
    tabs.value.push({ id: tabKey, name: payload.name, closeable: true })
  }
  activeTab.value = tabKey
  if (payload.woId) {
    currentWoId.value = payload.woId
  }
}

// Watch for tab changes to pass woId
defineExpose({ currentWoId })

const closeTab = (id: string) => {
  const idx = tabs.value.findIndex(t => t.id === id)
  if (idx > -1 && tabs.value[idx].closeable) {
    tabs.value.splice(idx, 1)
    if (activeTab.value === id) {
      activeTab.value = tabs.value[Math.min(idx, tabs.value.length - 1)]?.id || 'dashboard'
    }
  }
}

async function loadRecentNotifs() {
  const { data } = await (await import('./api')).default.get('/notifications', { params: { page_size: 5 } })
  recentNotifs.value = data.items
}

function handleNotifClick(n: any) {
  if (n.related_resource_type === 'work_order' && n.related_resource_id) {
    handleNavigate({ id: 'work-order-detail', name: '工单详情', woId: n.related_resource_id })
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --sidebar-width: 220px;
  --header-height: 56px;
  --tabs-height: 40px;
  --primary: #1890ff;
  --primary-dark: #096dd9;
  --success: #52c41a;
  --warning: #faad14;
  --danger: #ff4d4f;
  --purple: #722ed1;
  --bg-layout: #f0f2f5;
  --border: #e8e8e8;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', -apple-system, sans-serif; background: var(--bg-layout); }

.mes-layout { display: flex; height: 100vh; overflow: hidden; }

/* 侧边栏 */
.mes-sidebar {
  width: var(--sidebar-width); min-width: var(--sidebar-width);
  background: #001529; display: flex; flex-direction: column;
  box-shadow: 2px 0 8px rgba(0,0,0,.15);
}
.mes-logo {
  height: 64px; display: flex; align-items: center; padding: 0 20px;
  border-bottom: 1px solid rgba(255,255,255,.08);
}
.logo-icon { font-size: 28px; color: #1890ff; margin-right: 10px; }
.logo-text { color: #fff; font-size: 16px; font-weight: 600; letter-spacing: 1px; }
.mes-menu-wrapper { flex: 1; overflow-y: auto; padding: 8px 0; }
.mes-menu-wrapper .el-menu { border-right: none; }
.mes-menu-wrapper .el-menu-item { height: 44px; line-height: 44px; margin: 2px 8px; border-radius: 6px; }
.mes-menu-wrapper .el-menu-item.is-active { background: #1890ff !important; }
.mes-user-panel { padding: 12px 16px; border-top: 1px solid rgba(255,255,255,.08); }
.user-card { display: flex; align-items: center; gap: 10px; }
.user-name { color: #fff; font-size: 14px; font-weight: 500; }
.user-role { color: rgba(255,255,255,.45); font-size: 12px; }

/* 主体 */
.mes-main { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: var(--bg-layout); }
.mes-header {
  height: var(--header-height); background: #fff; padding: 0 24px;
  display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid var(--border); flex-shrink: 0;
}
.header-right { width: 260px; }
.search-input .el-input__wrapper { border-radius: 8px; }

/* Tab 栏 */
.mes-tabs {
  height: var(--tabs-height); background: #fff; display: flex; align-items: center;
  padding: 0 16px; gap: 4px; border-bottom: 1px solid var(--border); flex-shrink: 0;
}
.mes-tab-item {
  padding: 6px 16px; border-radius: 6px; cursor: pointer; font-size: 13px;
  color: #666; display: flex; align-items: center; gap: 6px; transition: all .2s;
}
.mes-tab-item:hover { background: #f5f5f5; }
.mes-tab-item.active { background: #e6f7ff; color: var(--primary); font-weight: 500; }
.mes-tab-item .el-icon { font-size: 12px; color: #999; }
.mes-tab-item .el-icon:hover { color: var(--danger); }

/* 内容区 */
.mes-content { flex: 1; overflow-y: auto; padding: 20px; }

/* 通用页面容器 */
.page-container {
  background: #fff; border-radius: 8px; padding: 20px 24px;
  border: 1px solid var(--border);
}
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid #f0f0f0;
}
.page-header h2 { font-size: 18px; font-weight: 600; color: #1a1a1a; }

/* 表格美化 */
.el-table { border-radius: 8px; overflow: hidden; }
.el-table th.el-table__cell { background: #fafafa !important; font-weight: 600; color: #333; font-size: 13px; }
.el-table td.el-table__cell { font-size: 13px; color: #555; }

/* 分页栏 */
.pagination-bar { display: flex; justify-content: flex-end; margin-top: 16px; }
</style>
