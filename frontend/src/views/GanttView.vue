<template>
  <div class="page-container">
    <div class="page-header">
      <h2>排程甘特图</h2>
      <div class="gantt-controls">
        <el-select v-model="selectedWoId" placeholder="全部工单" clearable style="width:240px" @change="loadData">
          <el-option v-for="wo in workOrderList" :key="wo.id" :label="`${wo.wo_number} - ${wo.project_name}`" :value="wo.id" />
        </el-select>
        <el-radio-group v-model="viewMode" size="small" @change="renderChart">
          <el-radio-button label="day">日</el-radio-button>
          <el-radio-button label="week">周</el-radio-button>
          <el-radio-button label="month">月</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <div class="gantt-wo-info" v-if="currentWo">
      <el-tag :type="currentWo.status === 'Completed' ? 'success' : currentWo.status === 'Blocked' ? 'danger' : 'primary'">
        {{ currentWo.wo_number }}
      </el-tag>
      <span class="wo-project">{{ currentWo.project_name }}</span>
      <el-progress :percentage="currentWo.total_progress" :stroke-width="8" style="width:160px" />
    </div>

    <div ref="chartRef" class="gantt-chart" v-loading="loading"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import { getGanttData, getWorkOrders } from '../api'

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null
const loading = ref(false)
const selectedWoId = ref<number | undefined>(undefined)
const viewMode = ref<'day' | 'week' | 'month'>('day')
const workOrderList = ref<any[]>([])
const allData = ref<any[]>([])

const currentWo = computed(() => {
  if (!selectedWoId.value) return null
  return allData.value.find(w => w.id === selectedWoId.value) || null
})

onMounted(async () => {
  await loadWorkOrders()
  await loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})

const handleResize = () => chart?.resize()

async function loadWorkOrders() {
  const data = await getWorkOrders({ page: 1, page_size: 200 })
  workOrderList.value = data.items || []
}

async function loadData() {
  loading.value = true
  try {
    allData.value = await getGanttData(selectedWoId.value)
    await nextTick()
    renderChart()
  } finally {
    loading.value = false
  }
}

function renderChart() {
  if (!chartRef.value || allData.value.length === 0) return
  if (!chart) chart = echarts.init(chartRef.value)

  const today = new Date()
  today.setHours(0, 0, 0, 0)

  // Collect all milestones into flat rows
  const rows: any[] = []
  let dateMin = Infinity
  let dateMax = -Infinity

  for (const wo of allData.value) {
    for (const m of wo.milestones) {
      const pStart = m.planned_start_date ? new Date(m.planned_start_date) : new Date(m.planned_end_date)
      const pEnd = new Date(m.planned_end_date)
      const aStart = m.actual_start_date ? new Date(m.actual_start_date) : null
      const aEnd = m.actual_end_date ? new Date(m.actual_end_date) : null

      dateMin = Math.min(dateMin, pStart.getTime(), aStart?.getTime() ?? Infinity)
      dateMax = Math.max(dateMax, pEnd.getTime(), aEnd?.getTime() ?? -Infinity)

      rows.push({
        label: `${wo.wo_number.substring(0, 15)} | ${m.node_name}`,
        fullName: `${wo.wo_number} - ${wo.project_name}`,
        nodeName: m.node_name,
        pStart, pEnd,
        aStart, aEnd,
        completionRate: m.completion_rate,
        status: m.status,
        deviationDays: m.deviation_days,
        plannedStart: m.planned_start_date,
        plannedEnd: m.planned_end_date,
        actualStart: m.actual_start_date,
        actualEnd: m.actual_end_date,
      })
    }
  }

  if (rows.length === 0) {
    chart.setOption({ title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#999', fontSize: 16 } } })
    return
  }

  // Add padding to date range
  const dayMs = 86400000
  const padDays = viewMode.value === 'day' ? 3 : viewMode.value === 'week' ? 14 : 30
  dateMin -= padDays * dayMs
  dateMax += padDays * dayMs

  // Y-axis labels
  const yLabels = rows.map((r, i) => {
    const check = r.status === 'Completed' ? '✅ ' : ''
    return check + r.label
  })

  // Series: planned (blue), actual (green)
  const plannedSeries = rows.map((r, i) => ({
    type: 'custom',
    renderItem: (_params: any, api: any) => {
      const categoryIndex = api.value(0)
      const start = api.coord([api.value(1), categoryIndex])
      const end = api.coord([api.value(2), categoryIndex])
      const barHeight = api.size([0, 1])[1] * 0.3
      const rectShape = echarts.graphic.clipRectByRect(
        { x: start[0], y: start[1] - barHeight / 2, width: end[0] - start[0], height: barHeight },
        { x: params2.coordSys.x, y: params2.coordSys.y, width: params2.coordSys.width, height: params2.coordSys.height }
      )
      return rectShape && { type: 'rect', transition: ['shape'], shape: rectShape, style: api.style() }
    },
    encode: { x: [1, 2], y: 0 },
    data: [[i, r.pStart.getTime(), r.pEnd.getTime()]],
    itemStyle: { color: r.deviationDays > 0 ? '#ff4d4f' : '#1890ff' },
    z: 2,
  }))

  // Build actual series
  const actualSeries: any[] = []
  rows.forEach((r, i) => {
    if (r.aStart && r.aEnd) {
      actualSeries.push({
        type: 'custom',
        renderItem: (_params: any, api: any) => {
          const categoryIndex = api.value(0)
          const start = api.coord([api.value(1), categoryIndex])
          const end = api.coord([api.value(2), categoryIndex])
          const barHeight = api.size([0, 1])[1] * 0.18
          const rectShape = echarts.graphic.clipRectByRect(
            { x: start[0], y: start[1] + barHeight / 4, width: end[0] - start[0], height: barHeight },
            { x: params2.coordSys.x, y: params2.coordSys.y, width: params2.coordSys.width, height: params2.coordSys.height }
          )
          return rectShape && { type: 'rect', transition: ['shape'], shape: rectShape, style: api.style() }
        },
        encode: { x: [1, 2], y: 0 },
        data: [[i, r.aStart.getTime(), r.aEnd.getTime()]],
        itemStyle: { color: '#52c41a' },
        z: 3,
      })
    }
  })

  // Today line
  const todaySeries = {
    type: 'custom',
    renderItem: (_params: any, api: any) => {
      const point = api.coord([api.value(0), 0])
      return {
        type: 'line',
        transition: ['shape'],
        shape: { x1: point[0], y1: params2.coordSys.y, x2: point[0], y2: params2.coordSys.y + params2.coordSys.height },
        style: { stroke: '#ff4d4f', lineDash: [6, 4], lineWidth: 2 },
      }
    },
    data: [[today.getTime()]],
    z: 10,
    silent: true,
  }

  // Compute time unit
  let interval: number
  let formatter: (d: number) => string
  if (viewMode.value === 'day') {
    interval = dayMs
    formatter = (d) => new Date(d).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  } else if (viewMode.value === 'week') {
    interval = 7 * dayMs
    formatter = (d) => new Date(d).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  } else {
    interval = 30 * dayMs
    formatter = (d) => new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'short' })
  }

  const params2: any = {} // placeholder for coordSys ref used in renderItem closures

  // Tooltip formatter
  const tooltipFormatter = (p: any) => {
    const row = rows[p.value[0]]
    if (!row) return ''
    return `<div style="font-size:13px;line-height:1.8">
      <strong>${row.fullName}</strong><br/>
      节点：${row.nodeName}<br/>
      计划：${row.plannedStart || '-'} ~ ${row.plannedEnd}<br/>
      实际：${row.actualStart || '-'} ~ ${row.actualEnd || '-'}<br/>
      偏差：<span style="color:${row.deviationDays > 0 ? '#ff4d4f' : '#52c41a'}">${row.deviationDays > 0 ? '+' : ''}${row.deviationDays}天</span><br/>
      完成率：${row.completionRate}%<br/>
      状态：${row.status}
    </div>`
  }

  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: tooltipFormatter,
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#e8e8e8',
      textStyle: { color: '#333' },
    },
    legend: {
      data: ['计划时段', '实际时段', '今日'],
      top: 0,
      textStyle: { fontSize: 12 },
    },
    dataZoom: [
      { type: 'slider', xAxisIndex: 0, bottom: 10, height: 20 },
      { type: 'inside', xAxisIndex: 0 },
    ],
    grid: { top: 50, left: 280, right: 30, bottom: 50, containLabel: false },
    xAxis: {
      type: 'value',
      min: dateMin,
      max: dateMax,
      axisLabel: { formatter, fontSize: 11 },
      splitLine: { show: true, lineStyle: { type: 'dashed', color: '#f0f0f0' } },
    },
    yAxis: {
      type: 'category',
      data: yLabels,
      axisLabel: { fontSize: 11, width: 270, overflow: 'truncate' },
      inverse: true,
    },
    series: [
      ...plannedSeries.map((s) => ({ name: '计划时段', ...s, renderItem: s.renderItem })),
      ...actualSeries.map((s) => ({ name: '实际时段', ...s })),
      { name: '今日', ...todaySeries, renderItem: todaySeries.renderItem },
    ],
  } as any, true)

  // Fix renderItem closures to capture coordSys
  chart.setOption({
    series: [
      ...plannedSeries.map((s) => ({
        name: '计划时段',
        type: 'custom',
        renderItem: (params: any, api: any) => {
          const categoryIndex = api.value(0)
          const start = api.coord([api.value(1), categoryIndex])
          const end = api.coord([api.value(2), categoryIndex])
          const barHeight = api.size([0, 1])[1] * 0.3
          const coordSys = params.coordSys
          const rectShape = echarts.graphic.clipRectByRect(
            { x: start[0], y: start[1] - barHeight / 2, width: end[0] - start[0], height: barHeight },
            { x: coordSys.x, y: coordSys.y, width: coordSys.width, height: coordSys.height }
          )
          return rectShape && { type: 'rect', transition: ['shape'], shape: rectShape, style: api.style() }
        },
        encode: { x: [1, 2], y: 0 },
        data: s.data,
        itemStyle: s.itemStyle,
        z: 2,
      })),
      ...actualSeries.map((s) => ({
        name: '实际时段',
        type: 'custom',
        renderItem: (params: any, api: any) => {
          const categoryIndex = api.value(0)
          const start = api.coord([api.value(1), categoryIndex])
          const end = api.coord([api.value(2), categoryIndex])
          const barHeight = api.size([0, 1])[1] * 0.18
          const coordSys = params.coordSys
          const rectShape = echarts.graphic.clipRectByRect(
            { x: start[0], y: start[1] + barHeight / 4, width: end[0] - start[0], height: barHeight },
            { x: coordSys.x, y: coordSys.y, width: coordSys.width, height: coordSys.height }
          )
          return rectShape && { type: 'rect', transition: ['shape'], shape: rectShape, style: api.style() }
        },
        encode: { x: [1, 2], y: 0 },
        data: s.data,
        itemStyle: s.itemStyle,
        z: 3,
      })),
      {
        name: '今日',
        type: 'custom',
        renderItem: (params: any, api: any) => {
          const point = api.coord([api.value(0), 0])
          const coordSys = params.coordSys
          return {
            type: 'line',
            transition: ['shape'],
            shape: { x1: point[0], y1: coordSys.y, x2: point[0], y2: coordSys.y + coordSys.height },
            style: { stroke: '#ff4d4f', lineDash: [6, 4], lineWidth: 2 },
          }
        },
        data: [[today.getTime()]],
        z: 10,
        silent: true,
      },
    ],
    tooltip: { trigger: 'item', formatter: tooltipFormatter, backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#e8e8e8', textStyle: { color: '#333' } },
    legend: { data: ['计划时段', '实际时段', '今日'], top: 0, textStyle: { fontSize: 12 } },
    dataZoom: [{ type: 'slider', xAxisIndex: 0, bottom: 10, height: 20 }, { type: 'inside', xAxisIndex: 0 }],
    grid: { top: 50, left: 280, right: 30, bottom: 50, containLabel: false },
    xAxis: { type: 'value', min: dateMin, max: dateMax, axisLabel: { formatter, fontSize: 11 }, splitLine: { show: true, lineStyle: { type: 'dashed', color: '#f0f0f0' } } },
    yAxis: { type: 'category', data: yLabels, axisLabel: { fontSize: 11, width: 270, overflow: 'truncate' }, inverse: true },
  }, true)
}
</script>

<style scoped>
.gantt-controls { display: flex; gap: 12px; align-items: center; }
.gantt-wo-info { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; padding: 10px 16px; background: #fafafa; border-radius: 6px; }
.wo-project { font-size: 14px; font-weight: 500; color: #333; }
.gantt-chart { width: 100%; height: calc(100vh - 300px); min-height: 400px; }
</style>
