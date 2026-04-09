<template>
  <div class="mes-layout">
    <aside class="mes-sidebar">
      <div class="mes-logo">
        <el-icon class="logo-icon"><Odometer /></el-icon>
        <span class="logo-text">MES 智造系统</span>
      </div>
      
      <div class="mes-menu-wrapper">
        <el-menu default-active="dashboard" background-color="#001529" text-color="#ffffffa6" active-text-color="#ffffff" @select="handleMenuSelect">
          <el-menu-item index="dashboard"><el-icon><Monitor /></el-icon>质量看板</el-menu-item>
          <el-menu-item index="work-orders"><el-icon><Memo /></el-icon>工单府库</el-menu-item>
          <el-menu-item index="drawings"><el-icon><EditPen /></el-icon>图纸中心</el-menu-item>
          <el-menu-item index="suppliers"><el-icon><ShoppingCart /></el-icon>供应商</el-menu-item>
          <el-menu-item index="quality-issues"><el-icon><Checked /></el-icon>不合格品项</el-menu-item>
          <el-menu-item index="users"><el-icon><User /></el-icon>吏部名册</el-menu-item>
        </el-menu>
      </div>

      <div class="mes-user-panel">
        <div class="user-card">
          <el-avatar :size="32">公</el-avatar>
          <div class="user-info"><div class="user-name">公子</div><div class="user-role">系统统领</div></div>
        </div>
      </div>
    </aside>

    <section class="mes-main">
      <header class="mes-header">
        <el-breadcrumb separator="/"><el-breadcrumb-item>MES</el-breadcrumb-item><el-breadcrumb-item>{{ activeTabName }}</el-breadcrumb-item></el-breadcrumb>
        <div class="header-right"><el-input placeholder="搜索 (Ctrl+K)" class="search-input" prefix-icon="Search" /></div>
      </header>

      <nav class="mes-tabs">
        <div v-for="tab in tabs" :key="tab.id" @click="activeTab = tab.id" :class="['mes-tab-item', activeTab === tab.id ? 'active' : '']">
          {{ tab.name }} <el-icon v-if="tab.closeable" @click.stop="closeTab(tab.id)"><Close /></el-icon>
        </div>
      </nav>

      <main class="mes-content">
        <transition name="el-fade-in" mode="out-in">
          <component :is="currentView" :key="activeTab" />
        </transition>
      </main>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineAsyncComponent, markRaw } from 'vue'
import { Monitor, Memo, User, Odometer, Search, Close, EditPen, ShoppingCart, Checked } from '@element-plus/icons-vue'

const Dashboard = markRaw(defineAsyncComponent(() => import('./views/Dashboard.vue')))
const WorkOrderList = markRaw(defineAsyncComponent(() => import('./views/WorkOrderList.vue')))
const UserList = markRaw(defineAsyncComponent(() => import('./views/UserList.vue')))
const QualityIssueList = markRaw(defineAsyncComponent(() => import('./views/QualityIssueList.vue')))
const DrawingList = markRaw(defineAsyncComponent(() => import('./views/DrawingList.vue')))
const SupplierList = markRaw(defineAsyncComponent(() => import('./views/SupplierList.vue')))

const activeTab = ref('dashboard')
const tabs = ref([{ id: 'dashboard', name: '质量看板', closeable: false }])

const currentView = computed(() => {
  const map: any = {
    'dashboard': Dashboard,
    'work-orders': WorkOrderList,
    'users': UserList,
    'quality-issues': QualityIssueList,
    'drawings': DrawingList,
    'suppliers': SupplierList
  }
  return map[activeTab.value] || Dashboard
})

const activeTabName = computed(() => tabs.value.find(t => t.id === activeTab.value)?.name || '')

const handleMenuSelect = (index: string) => {
  const existingTab = tabs.value.find(t => t.id === index)
  if (!existingTab) {
    const names: any = { 
      'dashboard': '质量看板', 'work-orders': '工单库', 'users': '名册',
      'drawings': '图纸中心', 'suppliers': '供应商', 'quality-issues': '不合格品'
    }
    tabs.value.push({ id: index, name: names[index], closeable: true })
  }
  activeTab.value = index
}

const closeTab = (id: string) => {
  const index = tabs.value.findIndex(t => t.id === id)
  if (index > -1) {
    tabs.value.splice(index, 1)
    if (activeTab.value === id) activeTab.value = tabs.value[tabs.value.length - 1].id
  }
}
</script>

<style scoped>
.mes-layout { display: flex; width: 100vw; height: 100vh; overflow: hidden; background: #f0f2f5; }
.mes-sidebar { width: 240px; background: #001529; display: flex; flex-direction: column; flex-shrink: 0; box-shadow: 2px 0 8px rgba(0,0,0,0.15); z-index: 100; }
.mes-logo { height: 64px; display: flex; align-items: center; padding: 0 24px; background: #002140; color: white; font-weight: bold; font-size: 18px; }
.logo-icon { font-size: 24px; margin-right: 12px; }
.mes-menu-wrapper { flex: 1; overflow-y: auto; }
.mes-user-panel { padding: 16px; border-top: 1px solid #000; }
.user-card { background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; display: flex; align-items: center; }
.user-info { margin-left: 12px; }
.user-name { color: white; font-size: 14px; font-weight: bold; }
.user-role { color: #ffffffa6; font-size: 12px; }
.mes-main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.mes-header { height: 64px; background: white; display: flex; justify-content: space-between; align-items: center; padding: 0 24px; border-bottom: 1px solid #f0f0f0; }
.mes-tabs { height: 40px; background: white; display: flex; align-items: center; padding: 0 16px; border-bottom: 1px solid #f0f0f0; }
.mes-tab-item { height: 100%; display: flex; align-items: center; padding: 0 16px; font-size: 12px; cursor: pointer; border-right: 1px solid #f0f0f0; transition: all 0.3s; }
.mes-tab-item.active { background: #e6f7ff; color: #1890ff; font-weight: bold; border-bottom: 2px solid #1890ff; }
.mes-content { flex: 1; overflow-y: auto; padding: 24px; }
</style>
