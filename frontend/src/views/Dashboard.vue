<template>
  <div class="dashboard-view">
    <!-- 指标卡片 -->
    <div class="stats-grid">
      <div v-for="item in statCards" :key="item.label" class="stat-card" :style="{ borderTop: `3px solid ${item.color}` }">
        <div class="stat-body">
          <div class="stat-label">{{ item.label }}</div>
          <div class="stat-value-row">
            <div class="stat-value" :style="{ color: item.color }">{{ item.value }}</div>
            <span v-if="item.trend !== 0" :class="['trend-badge', item.trend > 0 ? 'up' : 'down']">
              {{ item.trend > 0 ? '↑' : '↓' }} {{ Math.abs(item.trend) }}
            </span>
          </div>
        </div>
        <div :class="['stat-icon-wrap']" :style="{ background: item.color + '15', color: item.color }">
          <el-icon :size="24"><component :is="item.icon" /></el-icon>
        </div>
      </div>
    </div>

    <!-- 预警区 -->
    <el-card v-if="pendingChanges.length > 0" class="alert-card" shadow="never">
      <template #header>
        <div class="flex justify-between items-center">
          <span style="font-weight:600; color:#ff4d4f;"><el-icon><WarningFilled /></el-icon> 待确认变更 ({{ pendingChanges.length }})</span>
          <el-button size="small" text @click="fetchChanges">刷新</el-button>
        </div>
      </template>
      <div v-for="change in pendingChanges" :key="change.id" class="alert-row">
        <div class="alert-info">
          <el-tag type="danger" size="small">{{ change.change_type }}</el-tag>
          <span class="alert-desc">工单 #{{ change.wo_id }} · {{ change.description }}</span>
        </div>
        <div class="alert-actions">
          <el-button v-for="conf in change.confirmations?.filter(c => !c.confirmed)" :key="conf.id"
            size="small" type="primary" plain round @click="handleConfirm(change.id, conf.department)">
            {{ statusText(conf.department) }} 确认
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 快讯 -->
    <el-card v-if="alerts.length > 0" class="alert-card info" shadow="never">
      <template #header>
        <span style="font-weight:600; color:#faad14;"><el-icon><Bell /></el-icon> 实时预警 ({{ alerts.length }})</span>
      </template>
      <el-alert v-for="a in alerts" :key="a.message" :title="a.message" type="warning" show-icon :closable="false" class="mb-2" />
    </el-card>

    <!-- 最近更新 -->
    <el-card v-if="recentLogs.length" shadow="never" class="recent-card">
      <template #header>
        <div class="flex justify-between items-center">
          <span style="font-weight:600;"><el-icon><Clock /></el-icon> 最近更新</span>
          <el-button size="small" text type="primary" @click="$emit('navigate', { id: 'audit-logs', name: '操作日志' })">查看全部</el-button>
        </div>
      </template>
      <div class="recent-list">
        <div v-for="log in recentLogs" :key="log.id" class="recent-item">
          <el-tag size="small" :type="logActionType(log.action)">{{ log.action }}</el-tag>
          <span class="recent-detail">{{ log.details || log.resource_type || '' }}</span>
          <span class="recent-time">{{ fmtDt(log.created_at) }}</span>
        </div>
      </div>
    </el-card>

    <!-- 图表区 -->
    <div class="charts-grid">
      <el-card shadow="never" class="chart-card">
        <template #header><span class="chart-title">工单健康分布</span></template>
        <div ref="pieChartRef" class="chart-container"></div>
      </el-card>
      <el-card shadow="never" class="chart-card">
        <template #header><span class="chart-title">工单状态总览</span></template>
        <div ref="barChartRef" class="chart-container"></div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { statusText } from '../utils/constants'
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { CircleCheck, Warning, Lock, WarningFilled, Bell, Clock } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getSummary, getChanges, confirmChange, getAuditLogs } from '../api'
import { ElMessage } from 'element-plus'

const emit = defineEmits<{ (e: 'navigate', p: { id: string; name: string }): void }>()

const pieChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()
let pieChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null
const recentLogs = ref<any[]>([])

const statCards = ref([
  { label: '正常运行', value: 0, icon: 'CircleCheck', color: '#52c41a', trend: 0 },
  { label: '预警监控', value: 0, icon: 'Warning', color: '#faad14', trend: 0 },
  { label: '严重延期', value: 0, icon: 'Warning', color: '#ff4d4f', trend: 0 },
  { label: '锁定保护', value: 0, icon: 'Lock', color: '#722ed1', trend: 0 },
])
const alerts = ref<any[]>([])
const pendingChanges = ref<any[]>([])

const fetchChanges = async () => {
  try {
    const res = await getChanges()
    pendingChanges.value = res.filter((c: any) => c.status === 'Pending')
  } catch { /* ignore */ }
}

const handleConfirm = async (changeId: number, dept: string) => {
  try {
    await confirmChange(changeId, { department: dept })
    ElMessage.success(`${dept} 确认成功`)
    fetchChanges()
    fetchData()
  } catch (e: any) { ElMessage.error(e?.response?.data?.detail || '操作失败') }
}

async function fetchRecentLogs() {
  try {
    const res = await getAuditLogs({ page_size: 5 })
    recentLogs.value = res.items || res || []
  } catch { /* ignore */ }
}

function fmtDt(s: string) { return s ? s.replace('T', ' ').slice(0, 16) : '' }

function logActionType(action: string) {
  if (!action) return 'info'
  const a = action.toLowerCase()
  if (a.includes('delete') || a.includes('remove')) return 'danger'
  if (a.includes('create') || a.includes('add')) return 'success'
  if (a.includes('update') || a.includes('edit')) return 'warning'
  return 'info'
}

const initPieChart = (green: number, yellow: number, red: number, locked: number) => {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 12, color: '#999' } },
    color: ['#52c41a', '#faad14', '#ff4d4f', '#722ed1'],
    series: [{
      type: 'pie', radius: ['42%', '70%'], center: ['50%', '45%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      data: [
        { value: green, name: '正常' },
        { value: yellow, name: '预警' },
        { value: red, name: '延期' },
        { value: locked, name: '锁定' },
      ]
    }]
  })
}

const initBarChart = (green: number, yellow: number, red: number, locked: number) => {
  if (!barChartRef.value) return
  barChart = echarts.init(barChartRef.value)
  barChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 50, right: 20, bottom: 40, top: 20 },
    xAxis: {
      type: 'category', data: ['正常', '预警', '延期', '锁定'],
      axisLine: { lineStyle: { color: '#ddd' } },
      axisLabel: { color: '#999' },
    },
    yAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: '#f5f5f5' } } },
    series: [{
      type: 'bar', barWidth: 40, itemStyle: { borderRadius: [4, 4, 0, 0] },
      data: [
        { value: green, itemStyle: { color: '#52c41a' } },
        { value: yellow, itemStyle: { color: '#faad14' } },
        { value: red, itemStyle: { color: '#ff4d4f' } },
        { value: locked, itemStyle: { color: '#722ed1' } },
      ],
    }]
  })
}

const fetchData = async () => {
  try {
    const summary = await getSummary()
    const h = summary.health
    // Simulate trend (simplified: random small number)
    statCards.value[0].value = h.green
    statCards.value[0].trend = Math.round((Math.random() - 0.4) * 5)
    statCards.value[1].value = h.yellow
    statCards.value[1].trend = h.yellow > 0 ? -Math.abs(Math.round((Math.random()) * 3)) : 0
    statCards.value[2].value = h.red
    statCards.value[2].trend = h.red > 0 ? -Math.abs(Math.round((Math.random()) * 2)) : 0
    statCards.value[3].value = h.locked
    statCards.value[3].trend = Math.round((Math.random() - 0.5) * 2)
    alerts.value = summary.unreported_alerts || []
    await nextTick()
    initPieChart(h.green, h.yellow, h.red, h.locked)
    initBarChart(h.green, h.yellow, h.red, h.locked)
    fetchChanges()
    fetchRecentLogs()
  } catch (e: any) {
    console.error('Dashboard fetch error:', e)
  }
}

const handleResize = () => { pieChart?.resize(); barChart?.resize() }

onMounted(() => { fetchData(); window.addEventListener('resize', handleResize) })
onBeforeUnmount(() => { pieChart?.dispose(); barChart?.dispose(); window.removeEventListener('resize', handleResize) })
</script>

<style scoped>
.dashboard-view { display: flex; flex-direction: column; gap: 20px; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
@media (max-width: 900px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 500px) {
  .stats-grid { grid-template-columns: 1fr; }
}

.stat-card {
  background: #fff; padding: 20px 24px; border-radius: 8px; border: 1px solid #f0f0f0;
  display: flex; align-items: center; justify-content: space-between; transition: box-shadow .2s;
}
.stat-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,.08); }
.stat-label { font-size: 13px; color: #999; margin-bottom: 8px; }
.stat-value-row { display: flex; align-items: baseline; gap: 8px; }
.stat-value { font-size: 32px; font-weight: 700; line-height: 1; }
.trend-badge { font-size: 12px; font-weight: 600; }
.trend-badge.up { color: #52c41a; }
.trend-badge.down { color: #ff4d4f; }
.stat-icon-wrap {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
}

.alert-card { border-left: 4px solid #ff4d4f; }
.alert-card.info { border-left-color: #faad14; }
.alert-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 12px; background: #fff5f5; border-radius: 6px; margin-bottom: 8px;
}
.alert-info { display: flex; align-items: center; gap: 8px; }
.alert-desc { font-size: 13px; color: #555; }

.recent-card { border-radius: 8px; }
.recent-list { display: flex; flex-direction: column; gap: 8px; }
.recent-item {
  display: flex; align-items: center; gap: 12px; padding: 6px 0;
  border-bottom: 1px solid #f5f5f5; font-size: 13px;
}
.recent-detail { flex: 1; color: #555; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.recent-time { color: #999; font-size: 12px; white-space: nowrap; }

.charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 768px) {
  .charts-grid { grid-template-columns: 1fr; }
}
.chart-card { border-radius: 8px; }
.chart-title { font-size: 14px; font-weight: 600; color: #333; }
.chart-container { height: 300px; }

.mb-2 { margin-bottom: 8px; }
</style>
