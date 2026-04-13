<template>
  <Login v-if="!auth.isLoggedIn" @success="onLoginSuccess" />
  <BigScreen v-else-if="showBigScreen" @exit="showBigScreen=false" />
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
          <el-sub-menu index="system" v-if="auth.user?.role === 'Admin'">
            <template #title><el-icon><Setting /></el-icon>系统设置</template>
            <el-menu-item index="system-config">系统配置</el-menu-item>
            <el-menu-item index="departments">部门管理</el-menu-item>
            <el-menu-item index="templates">工单模板</el-menu-item>
          </el-sub-menu>
          <el-menu-item index="gantt" v-if="permStore.hasPermission('work_orders:read')"><el-icon><DataLine /></el-icon>排程甘特图</el-menu-item>
          <el-menu-item index="audit-logs" v-if="permStore.hasPermission('audit:read')"><el-icon><Document /></el-icon>操作日志</el-menu-item>
          <el-menu-item index="notifications"><el-icon><Bell /></el-icon>通知中心</el-menu-item>
          <el-menu-item index="task-board" v-if="permStore.hasPermission('work_orders:read')"><el-icon><DataLine /></el-icon>任务看板</el-menu-item>
          <el-menu-item index="approvals"><el-icon><DataLine /></el-icon>审批中心</el-menu-item>
          <el-menu-item index="exceptions"><el-icon><DataLine /></el-icon>异常管理</el-menu-item>
          <el-menu-item index="automation" v-if="auth.user?.role === 'Admin'"><el-icon><DataLine /></el-icon>自动化规则</el-menu-item>
          <el-menu-item index="collaboration" v-if="permStore.hasPermission('work_orders:read')"><el-icon><DataLine /></el-icon>协作面板</el-menu-item>
          <el-menu-item index="analytics" v-if="permStore.hasPermission('dashboard:read')"><el-icon><DataLine /></el-icon>数据分析</el-menu-item>
          <el-menu-item index="report-center" v-if="permStore.hasPermission('dashboard:read')"><el-icon><DataLine /></el-icon>报表中心</el-menu-item>
          <el-menu-item index="bigscreen" v-if="permStore.hasPermission('dashboard:read')"><el-icon><DataLine /></el-icon>数据大屏</el-menu-item>
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
          <!-- 全局搜索 -->
          <el-popover
            :width="420"
            trigger="focus"
            :visible="searchDropdownVisible"
            @update:visible="searchDropdownVisible = $event"
            popper-class="global-search-popper"
          >
            <template #reference>
              <el-input
                ref="globalSearchRef"
                v-model="globalSearchQuery"
                placeholder="全局搜索 (Ctrl+K)"
                class="search-input"
                prefix-icon="Search"
                clearable
                @input="debouncedGlobalSearch"
                @keyup.escape="clearGlobalSearch"
              />
            </template>
            <div v-if="globalSearching" style="text-align:center;padding:16px;color:#999;">
              <el-icon class="is-loading"><Loading /></el-icon> 搜索中...
            </div>
            <div v-else-if="globalSearchResults.length === 0 && globalSearchQuery" style="text-align:center;padding:16px;color:#999;">
              未找到相关工单
            </div>
            <div v-else-if="!globalSearchQuery" style="text-align:center;padding:12px;color:#bbb;">
              输入工单号、项目名或客户名搜索
            </div>
            <div v-else class="search-results">
              <div v-for="item in globalSearchResults" :key="item.id" class="search-result-item" @click="onSearchResultClick(item)">
                <div class="search-result-main">
                  <el-link type="primary" :underline="false">{{ item.wo_number }}</el-link>
                  <el-tag size="small" :type="statusTagType(item.status)" style="margin-left:8px;">{{ item.status }}</el-tag>
                </div>
                <div class="search-result-sub">{{ item.project_name }} · {{ item.customer_name }}</div>
              </div>
            </div>
          </el-popover>

          <span class="ws-indicator" :class="notifStore.wsStatus" title="WebSocket"></span>
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
import { ref, computed, onMounted, onBeforeUnmount, onErrorCaptured } from 'vue'
import { Monitor, Memo, User, Odometer, Search, Close, EditPen, ShoppingCart, Checked, Lock, Document, DataLine, Bell, Loading, Setting } from '@element-plus/icons-vue'
import { useAuthStore } from './stores/auth'
import { usePermissionStore } from './stores/permission'
import { useNotificationStore } from './stores/notification'
import Login from './views/Login.vue'
import BigScreen from './views/BigScreen.vue'
import Dashboard from './views/Dashboard.vue'
import WorkOrderList from './views/WorkOrderList.vue'
import UserList from './views/UserList.vue'
import QualityIssueList from './views/QualityIssueList.vue'
import DrawingList from './views/DrawingList.vue'
import SupplierList from './views/SupplierList.vue'
import WorkOrderDetail from './views/WorkOrderDetail.vue'
import PermissionManage from './views/PermissionManage.vue'
import AuditLogView from './views/AuditLog.vue'
import GanttView from './views/GanttView.vue'
import NotificationCenter from './views/NotificationCenter.vue'
import SystemConfigView from './views/SystemConfig.vue'
import DepartmentManageView from './views/DepartmentManage.vue'
import TemplateManageView from './views/TemplateManage.vue'
import TaskBoard from './views/TaskBoard.vue'
import ApprovalCenter from './views/ApprovalCenter.vue'
import ExceptionCenter from './views/ExceptionCenter.vue'
import CollaborationView from './views/CollaborationView.vue'
import AutomationRules from './views/AutomationRules.vue'
import AnalyticsDashboard from './views/AnalyticsDashboard.vue'
import ReportCenter from './views/ReportCenter.vue'
import { getWorkOrders, getBigscreenOverview } from './api'

// 全局错误捕获，防止子组件报错导致白屏
onErrorCaptured((err, instance, info) => {
  console.error('[App ErrorBoundary]', err, info)
  return false
})

const auth = useAuthStore()
const permStore = usePermissionStore()
const notifStore = useNotificationStore()
const notifDropdown = ref(false)
const recentNotifs = ref<any[]>([])

onMounted(async () => {
  if (auth.isLoggedIn) {
    await initializeSession()
    notifStore.connectWs()
  }
})

onBeforeUnmount(() => {
  notifStore.disconnectWs()
})

// ── 全局搜索 ──
const globalSearchRef = ref<any>(null)
const globalSearchQuery = ref('')
const globalSearchResults = ref<any[]>([])
const globalSearching = ref(false)
const searchDropdownVisible = ref(false)

let searchTimer: ReturnType<typeof setTimeout> | null = null
function debouncedGlobalSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(doGlobalSearch, 300)
}

async function doGlobalSearch() {
  const q = globalSearchQuery.value.trim()
  if (!q) { globalSearchResults.value = []; return }
  globalSearching.value = true
  try {
    const res = await getWorkOrders({ keyword: q, page_size: 10 })
    globalSearchResults.value = res.items || []
  } catch { globalSearchResults.value = [] }
  finally { globalSearching.value = false }
}

function onSearchResultClick(item: any) {
  searchDropdownVisible.value = false
  globalSearchQuery.value = ''
  handleNavigate({ id: `wo-detail-${item.id}`, name: `工单 ${item.wo_number}`, woId: item.id })
}

function clearGlobalSearch() {
  globalSearchQuery.value = ''
  globalSearchResults.value = []
}

// Ctrl+K shortcut
function onGlobalKeyDown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    globalSearchRef.value?.focus()
  }
}
onMounted(() => window.addEventListener('keydown', onGlobalKeyDown))
onBeforeUnmount(() => window.removeEventListener('keydown', onGlobalKeyDown))

function statusTagType(s: string) {
  return ({ Backlog: 'info', InProgress: 'primary', Blocked: 'danger', Completed: 'success', Archived: 'info' } as any)[s] || 'info'
}

// Listen for notification navigation
window.addEventListener('notification-navigate', ((e: any) => {
  if (e.detail.type === 'work_order') {
    handleNavigate({ id: 'work-order-detail', name: '工单详情', woId: e.detail.id })
  }
}) as EventListener)

async function initializeSession() {
  try {
    await auth.fetchMe()
    if (auth.user?.role) {
      await permStore.loadForRole(auth.user.role)
    }
  } catch {
    permStore.clear()
    auth.logout()
  }
}

async function onLoginSuccess() {
  await initializeSession()
  notifStore.connectWs()
}


const showBigScreen = ref(false)
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
    'system-config': SystemConfigView,
    'departments': DepartmentManageView,
    'templates': TemplateManageView,
    'task-board': TaskBoard,
    'approvals': ApprovalCenter,
    'exceptions': ExceptionCenter,
    'collaboration': CollaborationView,
    'automation': AutomationRules,
    'analytics': AnalyticsDashboard,
    'report-center': ReportCenter,
  }
  return map[activeTab.value] || Dashboard
})

const currentWoId = ref<number | undefined>(undefined)

const activeTabName = computed(() => tabs.value.find(t => t.id === activeTab.value)?.name || '')

const handleMenuSelect = (index: string) => {
  if (index === 'bigscreen') {
    showBigScreen.value = true
    return
  }
  const existingTab = tabs.value.find(t => t.id === index)
  if (!existingTab) {
    const names: any = {
      'dashboard': '质量看板', 'work-orders': '工单府库', 'users': '吏部名册',
      'quality-issues': '不合格品项', 'drawings': '图纸中心', 'suppliers': '供应商',
      'permissions': '权限管理',
      'system-config': '系统配置',
      'departments': '部门管理',
      'templates': '工单模板',
      'audit-logs': '操作日志',
      'gantt': '排程甘特图',
      'notifications': '通知中心',
      'task-board': '任务看板',
      'approvals': '审批中心',
      'exceptions': '异常管理',
      'automation': '自动化规则',
      'collaboration': '协作面板',
      'analytics': '数据分析',
      'report-center': '报表中心',
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
.header-right { width: 320px; display: flex; gap: 8px; align-items: center; }
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

/* 全局搜索结果 */
.search-results { max-height: 360px; overflow-y: auto; }
.search-result-item {
  padding: 10px 12px; border-radius: 6px; cursor: pointer;
  transition: background .2s;
}
.search-result-item:hover { background: #f5f5f5; }
.search-result-main { display: flex; align-items: center; margin-bottom: 2px; }
.search-result-sub { font-size: 12px; color: #999; }

/* WebSocket indicator */
.ws-indicator {
  display: inline-block; width: 8px; height: 8px; border-radius: 50%;
  margin-right: 4px; vertical-align: middle;
}
.ws-indicator.connected { background: #52c41a; }
.ws-indicator.disconnected { background: #ff4d4f; }
.ws-indicator.reconnecting { background: #faad14; animation: pulse 1s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
</style>
