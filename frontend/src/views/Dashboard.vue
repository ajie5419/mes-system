<template>
  <div class="dashboard-view">
    <div class="stats-grid">
      <div v-for="item in statCards" :key="item.label" class="stat-card shadow-sm">
        <div :class="['stat-icon', item.bg]"><el-icon><component :is="item.icon" /></el-icon></div>
        <div class="stat-info"><div class="stat-label">{{ item.label }}</div><div class="stat-value">{{ item.value }}</div></div>
      </div>
    </div>

    <!-- 待办任务：变更确认区 -->
    <el-card v-if="pendingChanges.length > 0" class="mb-6 border-l-4 border-red-500 shadow-sm">
      <template #header><div class="flex justify-between items-center font-bold text-red-600"><span>待确认变更 (需各部签押)</span><el-button size="small" @click="fetchChanges">刷新待办</el-button></div></template>
      <div v-for="change in pendingChanges" :key="change.id" class="p-4 bg-red-50 rounded-lg mb-2 flex justify-between items-center">
        <div>
          <el-tag type="danger" class="mr-2">{{ change.change_type }}</el-tag>
          <span class="text-sm font-medium">工单 ID: {{ change.wo_id }} | 描述: {{ change.description }}</span>
        </div>
        <div class="flex gap-2">
          <el-button v-for="conf in change.confirmations.filter(c => !c.confirmed)" :key="conf.id" size="small" type="primary" plain @click="handleConfirm(change.id, conf.department)">
            {{ conf.department }}确认
          </el-button>
        </div>
      </div>
    </el-card>

    <div class="charts-grid">
      <div class="chart-box"><div class="chart-header">工单健康分布</div><div id="pie-chart" class="chart-container"></div></div>
      <div class="chart-box main-chart"><div class="chart-header">系统实时快讯</div>
        <el-alert v-for="a in alerts" :key="a.message" :title="a.message" type="warning" show-icon class="mb-2" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { CircleCheck, Warning, Lock } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getSummary, getChanges, confirmChange } from '../api'
import { ElMessage } from 'element-plus'

const statCards = ref([
  { label: '正常运行', value: 0, icon: 'CircleCheck', bg: 'green' },
  { label: '预警监控', value: 0, icon: 'Warning', bg: 'yellow' },
  { label: '严重延期', value: 0, icon: 'Warning', bg: 'red' },
  { label: '锁定保护', value: 0, icon: 'Lock', bg: 'indigo' }
])
const alerts = ref([])
const pendingChanges = ref([])

const fetchChanges = async () => {
  const res = await getChanges()
  pendingChanges.value = res.filter(c => c.status === 'Pending')
}

const handleConfirm = async (changeId, dept) => {
  await confirmChange(changeId, { department: dept })
  ElMessage.success(`${dept} 确认成功`)
  fetchChanges()
  fetchData()
}

const fetchData = async () => {
  const summary = await getSummary()
  statCards.value[0].value = summary.health.green
  statCards.value[1].value = summary.health.yellow
  statCards.value[2].value = summary.health.red
  statCards.value[3].value = summary.health.locked
  alerts.value = summary.unreported_alerts
  fetchChanges()
}

onMounted(fetchData)
</script>

<style scoped>
.dashboard-view { display: flex; flex-direction: column; gap: 24px; }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.stat-card { background: white; padding: 20px; border-radius: 12px; display: flex; align-items: center; border: 1px solid #f0f0f0; }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: white; margin-right: 16px; }
.stat-icon.green { background: #52c41a; }
.stat-icon.yellow { background: #faad14; }
.stat-icon.red { background: #ff4d4f; }
.stat-icon.indigo { background: #722ed1; }
.stat-value { font-size: 24px; font-weight: bold; margin-left: auto; }
.charts-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 24px; }
.chart-box { background: white; border-radius: 12px; border: 1px solid #f0f0f0; padding: 20px; }
.chart-header { font-size: 16px; font-weight: bold; margin-bottom: 20px; }
.chart-container { height: 300px; }
</style>
