<template>
  <div class="bigscreen-root">
    <!-- 顶部 -->
    <div class="bs-header">
      <el-button class="bs-exit-btn" type="info" plain size="small" @click="$emit('exit')">
        <el-icon><Close /></el-icon> 退出大屏
      </el-button>
      <div class="bs-title">MES 智造系统 · 数据驾驶舱</div>
      <div class="bs-datetime">{{ currentTime }}</div>
    </div>

    <!-- 主体 -->
    <div class="bs-body">
      <!-- 指标卡 -->
      <div class="bs-metrics">
        <div v-for="(m, i) in metrics" :key="m.key" class="bs-metric-card fade-up" :style="{ animationDelay: `${i * 0.1}s` }">
          <div class="bs-metric-icon" :style="{ color: m.color }">
            <el-icon :size="28"><component :is="m.icon" /></el-icon>
          </div>
          <div class="bs-metric-value" :style="{ color: m.color }">{{ m.value }}</div>
          <div class="bs-metric-label">{{ m.label }}</div>
        </div>
      </div>

      <!-- 图表第一行 -->
      <div class="bs-chart-row">
        <div class="bs-chart-card fade-up" style="animation-delay:0.3s">
          <div class="bs-chart-title">工单状态分布</div>
          <div ref="statusChartRef" class="bs-chart-box"></div>
        </div>
        <div class="bs-chart-card fade-up" style="animation-delay:0.4s">
          <div class="bs-chart-title">近 7 天趋势</div>
          <div ref="trendChartRef" class="bs-chart-box"></div>
        </div>
        <div class="bs-chart-card fade-up" style="animation-delay:0.5s">
          <div class="bs-chart-title">健康度分布</div>
          <div ref="healthChartRef" class="bs-chart-box"></div>
        </div>
      </div>

      <!-- 图表第二行 -->
      <div class="bs-chart-row">
        <div class="bs-chart-card fade-up" style="animation-delay:0.6s">
          <div class="bs-chart-title">部门工单分布</div>
          <div ref="deptChartRef" class="bs-chart-box"></div>
        </div>
        <div class="bs-chart-card fade-up" style="animation-delay:0.7s">
          <div class="bs-chart-title">优先级分布</div>
          <div ref="priorityChartRef" class="bs-chart-box"></div>
        </div>
        <div class="bs-chart-card fade-up" style="animation-delay:0.8s">
          <div class="bs-chart-title">最近操作日志</div>
          <div class="bs-log-list">
            <div v-if="data.recent_logs && data.recent_logs.length" class="bs-log-scroll">
              <!-- Duplicate for seamless scroll -->
              <div v-for="log in [...data.recent_logs, ...data.recent_logs]" :key="log.id + '-' + Math.random()" class="bs-log-item">
                <span>{{ log.username }} · {{ log.action }} · {{ log.resource_type }}</span>
                <span class="log-time">{{ log.created_at }}</span>
              </div>
            </div>
            <div v-else style="text-align:center;color:#667;padding:20px;">暂无日志</div>
          </div>
        </div>
      </div>

      <!-- 底部预警 -->
      <div class="bs-alert-bar">
        <div class="bs-alert-scroll">
          <span v-if="data.overdue > 0" class="bs-alert-item">
            <span class="bs-alert-dot"></span>
            当前有 {{ data.overdue }} 个工单延期未完成，请及时处理
          </span>
          <span v-else class="bs-alert-item" style="color:#86efac;">
            ✓ 所有工单运行正常，暂无预警
          </span>
          <span v-if="data.overdue_rate > 10" class="bs-alert-item">
            <span class="bs-alert-dot"></span>
            延期率已达 {{ data.overdue_rate }}%，请关注生产进度
          </span>
          <span v-if="data.today_new > 0" class="bs-alert-item">
            今日新增工单 {{ data.today_new }} 个
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { Close, DataLine, Loading, CircleCheckFilled, WarningFilled, Plus, Finished } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getBigscreenOverview } from '../api'

defineEmits(['exit'])

const data = reactive<any>({})
const currentTime = ref('')
const refreshTimer = ref<any>(null)
const clockTimer = ref<any>(null)

// Chart refs
const statusChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
const healthChartRef = ref<HTMLElement>()
const deptChartRef = ref<HTMLElement>()
const priorityChartRef = ref<HTMLElement>()

let charts: echarts.ECharts[] = []

const metrics = ref<any[]>([])

function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
  })
}

function buildMetrics() {
  metrics.value = [
    { key: 'total', label: '工单总数', value: data.total ?? 0, color: '#60a5fa', icon: DataLine },
    { key: 'in_progress', label: '进行中', value: data.in_progress ?? 0, color: '#34d399', icon: Loading },
    { key: 'completed', label: '已完成', value: data.completed ?? 0, color: '#fbbf24', icon: CircleCheckFilled },
    { key: 'overdue', label: '延期预警', value: data.overdue ?? 0, color: '#f87171', icon: WarningFilled },
    { key: 'today_new', label: '今日新增', value: data.today_new ?? 0, color: '#22d3ee', icon: Plus },
    { key: 'today_done', label: '今日完工', value: data.today_done ?? 0, color: '#a78bfa', icon: Finished },
  ]
}

function initCharts() {
  charts.forEach(c => c.dispose())
  charts = []

  const textColor = 'rgba(148,163,184,0.7)'
  const bluePalette = ['#3b82f6', '#60a5fa', '#93c5fd', '#2563eb', '#1d4ed8']

  // ── 状态分布 (环形图) ──
  if (statusChartRef.value) {
    const c = echarts.init(statusChartRef.value)
    charts.push(c)
    c.setOption({
      tooltip: { trigger: 'item', backgroundColor: 'rgba(15,23,42,0.9)', borderColor: '#3b82f6' },
      legend: { bottom: 4, textStyle: { color: textColor, fontSize: 11 }, itemWidth: 12, itemHeight: 12 },
      graphic: [{
        type: 'text', left: 'center', top: '38%',
        style: { text: String(data.total ?? 0), fill: '#e0e6f0', fontSize: 28, fontWeight: 'bold' }
      }, {
        type: 'text', left: 'center', top: '52%',
        style: { text: '总工单', fill: textColor, fontSize: 11 }
      }],
      series: [{
        type: 'pie', radius: ['42%', '62%'], center: ['50%', '48%'],
        label: { show: false },
        data: [
          { value: data.in_progress ?? 0, name: '进行中', itemStyle: { color: '#34d399' } },
          { value: data.completed ?? 0, name: '已完成', itemStyle: { color: '#fbbf24' } },
          { value: data.overdue ?? 0, name: '延期', itemStyle: { color: '#f87171' } },
          { value: Math.max(0, (data.total ?? 0) - (data.in_progress ?? 0) - (data.completed ?? 0) - (data.overdue ?? 0)), name: '其他', itemStyle: { color: '#64748b' } },
        ],
        animationType: 'scale',
        animationEasing: 'elasticOut',
      }]
    })
  }

  // ── 趋势双线图 ──
  if (trendChartRef.value && data.trend) {
    const c = echarts.init(trendChartRef.value)
    charts.push(c)
    c.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,23,42,0.9)', borderColor: '#3b82f6' },
      legend: { data: ['新增', '完工'], top: 0, textStyle: { color: textColor, fontSize: 11 } },
      grid: { left: 36, right: 16, top: 32, bottom: 24 },
      xAxis: {
        type: 'category', data: data.trend.map((t: any) => t.date),
        axisLine: { lineStyle: { color: 'rgba(59,130,246,0.2)' } },
        axisLabel: { color: textColor, fontSize: 11 },
      },
      yAxis: {
        type: 'value', minInterval: 1,
        splitLine: { lineStyle: { color: 'rgba(59,130,246,0.08)' } },
        axisLabel: { color: textColor, fontSize: 11 },
      },
      series: [
        {
          name: '新增', type: 'line', smooth: true,
          data: data.trend.map((t: any) => t.new),
          lineStyle: { color: '#60a5fa', width: 2 },
          itemStyle: { color: '#60a5fa' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(96,165,250,0.3)' },
              { offset: 1, color: 'rgba(96,165,250,0.02)' },
            ])
          },
          animationDuration: 1500,
        },
        {
          name: '完工', type: 'line', smooth: true,
          data: data.trend.map((t: any) => t.completed),
          lineStyle: { color: '#34d399', width: 2 },
          itemStyle: { color: '#34d399' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(52,211,153,0.3)' },
              { offset: 1, color: 'rgba(52,211,153,0.02)' },
            ])
          },
          animationDuration: 1800,
        }
      ]
    })
  }

  // ── 健康度仪表盘 ──
  if (healthChartRef.value) {
    const hd = data.health_distribution || {}
    const green = hd.GREEN || 0
    const yellow = hd.YELLOW || 0
    const red = hd.RED || 0
    const total = green + yellow + red || 1
    const healthyPercent = Math.round(green / total * 100)
    const c = echarts.init(healthChartRef.value)
    charts.push(c)
    c.setOption({
      series: [{
        type: 'gauge',
        startAngle: 220, endAngle: -40,
        min: 0, max: 100,
        splitNumber: 5,
        radius: '85%',
        progress: {
          show: true, width: 16,
          itemStyle: { color: healthyPercent >= 70 ? '#34d399' : healthyPercent >= 40 ? '#fbbf24' : '#f87171' }
        },
        axisLine: { lineStyle: { width: 16, color: [[1, 'rgba(59,130,246,0.1)']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: false },
        title: { show: true, offsetCenter: [0, '60%'], fontSize: 13, color: textColor },
        detail: {
          valueAnimation: true, offsetCenter: [0, '10%'],
          fontSize: 32, fontWeight: 'bold', color: '#e0e6f0',
          formatter: '{value}%'
        },
        data: [{ value: healthyPercent, name: '健康工单占比' }],
        animationDuration: 2000,
      }]
    })
  }

  // ── 部门柱状图 ──
  if (deptChartRef.value && data.department_distribution) {
    const dd = data.department_distribution
    const keys = Object.keys(dd)
    const vals = Object.values(dd)
    const c = echarts.init(deptChartRef.value)
    charts.push(c)
    c.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,23,42,0.9)', borderColor: '#3b82f6' },
      grid: { left: 80, right: 24, top: 8, bottom: 8 },
      xAxis: { type: 'value', minInterval: 1, axisLabel: { color: textColor, fontSize: 11 }, splitLine: { lineStyle: { color: 'rgba(59,130,246,0.08)' } } },
      yAxis: { type: 'category', data: keys, axisLine: { lineStyle: { color: 'rgba(59,130,246,0.2)' } }, axisLabel: { color: textColor, fontSize: 11 } },
      series: [{
        type: 'bar', data: vals, barWidth: 16, itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#1d4ed8' },
            { offset: 1, color: '#60a5fa' },
          ]),
          borderRadius: [0, 4, 4, 0],
        },
        animationDuration: 1500,
      }]
    })
  }

  // ── 优先级饼图 ──
  if (priorityChartRef.value && data.priority_distribution) {
    const pd = data.priority_distribution
    const pNames: any = { '1': '紧急', '2': '高', '3': '中', '4': '低', '5': '最低' }
    const pColors: any = { '1': '#f87171', '2': '#fbbf24', '3': '#60a5fa', '4': '#34d399', '5': '#64748b' }
    const pieData = Object.entries(pd).map(([k, v]) => ({
      name: pNames[k] || k, value: v,
      itemStyle: { color: pColors[k] || '#64748b' }
    }))
    const c = echarts.init(priorityChartRef.value)
    charts.push(c)
    c.setOption({
      tooltip: { trigger: 'item', backgroundColor: 'rgba(15,23,42,0.9)', borderColor: '#3b82f6' },
      legend: { bottom: 4, textStyle: { color: textColor, fontSize: 11 }, itemWidth: 12, itemHeight: 12 },
      series: [{
        type: 'pie', radius: ['28%', '55%'], center: ['50%', '44%'],
        label: { color: textColor, fontSize: 11 },
        data: pieData,
        animationType: 'scale',
        animationEasing: 'elasticOut',
      }]
    })
  }
}

async function loadData() {
  try {
    const res = await getBigscreenOverview()
    Object.assign(data, res)
    buildMetrics()
    await nextTick()
    initCharts()
  } catch (e) {
    console.error('大屏数据加载失败', e)
  }
}

function handleResize() {
  charts.forEach(c => c.resize())
}

onMounted(() => {
  updateClock()
  clockTimer.value = setInterval(updateClock, 1000)
  loadData()
  refreshTimer.value = setInterval(loadData, 60000)
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  clearInterval(clockTimer.value)
  clearInterval(refreshTimer.value)
  window.removeEventListener('resize', handleResize)
  charts.forEach(c => c.dispose())
})
</script>

<style scoped>
@import '../styles/bigscreen.css';
</style>
