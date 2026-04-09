<template>
  <div class="analytics-dashboard">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-radio-group v-model="timeRange" size="small" @change="fetchData">
        <el-radio-button label="7">近7天</el-radio-button>
        <el-radio-button label="30">近30天</el-radio-button>
        <el-radio-button label="90">近90天</el-radio-button>
      </el-radio-group>
      <el-date-picker v-model="customRange" type="daterange" size="small" range-separator="至"
        start-placeholder="开始" end-placeholder="结束" value-format="YYYY-MM-DD"
        style="width:260px;margin-left:12px;" @change="fetchData" />
    </div>

    <!-- KPI 卡片 -->
    <div class="kpi-row">
      <div class="kpi-card" v-for="k in kpis" :key="k.label">
        <div class="kpi-value" :style="{ color: k.color }">{{ k.value }}{{ k.suffix }}</div>
        <div class="kpi-label">{{ k.label }}</div>
      </div>
    </div>

    <!-- 图表行1 -->
    <div class="chart-row">
      <div class="chart-card"><div class="chart-title">工单完成趋势</div><div ref="trendRef" class="chart-box"></div></div>
      <div class="chart-card"><div class="chart-title">工单周期分布</div><div ref="cycleRef" class="chart-box"></div></div>
    </div>

    <!-- 图表行2 -->
    <div class="chart-row">
      <div class="chart-card"><div class="chart-title">部门工作量对比</div><div ref="workloadRef" class="chart-box"></div></div>
      <div class="chart-card"><div class="chart-title">部门效率雷达</div><div ref="efficiencyRef" class="chart-box"></div></div>
    </div>

    <!-- 图表行3 -->
    <div class="chart-row">
      <div class="chart-card"><div class="chart-title">异常趋势</div><div ref="excTrendRef" class="chart-box"></div></div>
      <div class="chart-card"><div class="chart-title">异常类型分布</div><div ref="excTypeRef" class="chart-box"></div></div>
    </div>

    <!-- 图表行4 -->
    <div class="chart-row">
      <div class="chart-card"><div class="chart-title">里程碑完成率排名</div><div ref="milestoneRef" class="chart-box"></div></div>
      <div class="chart-card"><div class="chart-title">进度汇报热力图</div><div ref="heatmapRef" class="chart-box"></div></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getAnalyticsKPI, getWOTrend, getWOCycleTime, getDeptWorkload, getDeptEfficiency, getExceptionTrend, getExceptionByType, getMilestoneCompletion, getProgressStreak } from '../api'

const timeRange = ref('30')
const customRange = ref(null)
const trendRef = ref<HTMLElement>()
const cycleRef = ref<HTMLElement>()
const workloadRef = ref<HTMLElement>()
const efficiencyRef = ref<HTMLElement>()
const excTrendRef = ref<HTMLElement>()
const excTypeRef = ref<HTMLElement>()
const milestoneRef = ref<HTMLElement>()
const heatmapRef = ref<HTMLElement>()

const kpis = ref<any[]>([])

function getDateRange() {
  if (customRange.value) return customRange.value
  const d = new Date()
  const end = d.toISOString().slice(0, 10)
  const start = new Date(d.getTime() - parseInt(timeRange.value) * 86400000).toISOString().slice(0, 10)
  return [start, end]
}

async function fetchData() {
  const [s, e] = getDateRange()
  const promises = [
    getAnalyticsKPI(),
    getWOTrend({ start_date: s, end_date: e }),
    getWOCycleTime(),
    getDeptWorkload(),
    getDeptEfficiency(),
    getExceptionTrend({ days: parseInt(timeRange.value) }),
    getExceptionByType(),
    getMilestoneCompletion(),
    getProgressStreak({ days: parseInt(timeRange.value) }),
  ]
  const [kpi, trend, cycle, workload, eff, excTrend, excType, milestone, streak] = await Promise.all(promises)

  kpis.value = [
    { label: '按时交付率', value: kpi.on_time_delivery_rate, suffix: '%', color: '#67c23a' },
    { label: '平均周期', value: kpi.avg_cycle_days, suffix: '天', color: '#409eff' },
    { label: '异常总数', value: kpi.total_exceptions, suffix: '', color: '#e6a23c' },
    { label: '异常解决率', value: kpi.exception_resolution_rate, suffix: '%', color: '#f56c6c' },
    { label: '延期工单', value: kpi.overdue_work_orders, suffix: '', color: '#f56c6c' },
    { label: '里程碑完成率', value: kpi.milestone_completion_rate, suffix: '%', color: '#67c23a' },
  ]

  await nextTick()
  renderTrend(trend)
  renderCycle(cycle)
  renderWorkload(workload)
  renderEfficiency(eff)
  renderExcTrend(excTrend)
  renderExcType(excType)
  renderMilestone(milestone)
  renderHeatmap(streak?.calendar || [])
}

function renderTrend(data: any[]) {
  const c = echarts.init(trendRef.value!)
  c.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['新增', '完成'], bottom: 0 },
    xAxis: { type: 'category', data: data.map(d => d.date) },
    yAxis: { type: 'value' },
    series: [
      { name: '新增', type: 'line', data: data.map(d => d.created), smooth: true, itemStyle: { color: '#409eff' } },
      { name: '完成', type: 'line', data: data.map(d => d.completed), smooth: true, itemStyle: { color: '#67c23a' } },
    ],
    grid: { left: 40, right: 20, top: 20, bottom: 40 }
  })
}

function renderCycle(data: any) {
  const dist = data.distribution || {}
  const c = echarts.init(cycleRef.value!)
  c.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: Object.keys(dist) },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: Object.values(dist), itemStyle: { color: '#409eff' } }],
    grid: { left: 40, right: 20, top: 20, bottom: 20 }
  })
}

function renderWorkload(data: any[]) {
  const c = echarts.init(workloadRef.value!)
  c.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['进行中', '待办', '已完成'], bottom: 0 },
    xAxis: { type: 'category', data: data.map(d => d.department) },
    yAxis: { type: 'value' },
    series: [
      { name: '进行中', type: 'bar', stack: 'a', data: data.map(d => d.in_progress), itemStyle: { color: '#409eff' } },
      { name: '待办', type: 'bar', stack: 'a', data: data.map(d => d.backlog), itemStyle: { color: '#e6a23c' } },
      { name: '已完成', type: 'bar', stack: 'a', data: data.map(d => d.completed), itemStyle: { color: '#67c23a' } },
    ],
    grid: { left: 40, right: 20, top: 20, bottom: 40 }
  })
}

function renderEfficiency(data: any[]) {
  const c = echarts.init(efficiencyRef.value!)
  c.setOption({
    tooltip: {},
    radar: {
      indicator: data.map(d => ({ name: d.department, max: 100 })),
    },
    series: [{
      type: 'radar',
      data: [{ value: data.map(d => d.completion_rate), name: '完成率', areaStyle: { opacity: 0.3 } }]
    }]
  })
}

function renderExcTrend(data: any[]) {
  const c = echarts.init(excTrendRef.value!)
  c.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['总数', '已解决'], bottom: 0 },
    xAxis: { type: 'category', data: data.map(d => d.date) },
    yAxis: { type: 'value' },
    series: [
      { name: '总数', type: 'line', areaStyle: { opacity: 0.3 }, data: data.map(d => d.count), itemStyle: { color: '#f56c6c' } },
      { name: '已解决', type: 'line', areaStyle: { opacity: 0.3 }, data: data.map(d => d.resolved), itemStyle: { color: '#67c23a' } },
    ],
    grid: { left: 40, right: 20, top: 20, bottom: 40 }
  })
}

function renderExcType(data: any[]) {
  const c = echarts.init(excTypeRef.value!)
  c.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: data.map(d => ({ value: d.count, name: d.type })),
      label: { show: true, formatter: '{b}: {c}' }
    }]
  })
}

function renderMilestone(data: any[]) {
  const sorted = [...data].reverse()
  const c = echarts.init(milestoneRef.value!)
  c.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value', max: 100 },
    yAxis: { type: 'category', data: sorted.map(d => d.node_name) },
    series: [{ type: 'bar', data: sorted.map(d => d.rate), itemStyle: { color: '#409eff' }, label: { show: true, position: 'right', formatter: '{c}%' } }],
    grid: { left: 80, right: 50, top: 10, bottom: 20 }
  })
}

function renderHeatmap(calendar: any[]) {
  const c = echarts.init(heatmapRef.value!)
  const data = calendar.map(d => [d.date, d.has_report ? 1 : 0, d.count])
  const dates = data.map(d => d[0])
  c.setOption({
    tooltip: { formatter: (p: any) => `${p.value[0]}: ${p.value[2]} 次汇报` },
    visualMap: { min: 0, max: 1, show: false, inRange: { color: ['#ebeef5', '#409eff'] } },
    xAxis: { type: 'category', data: dates, show: false },
    yAxis: { type: 'category', data: ['汇报'], show: false },
    series: [{
      type: 'heatmap',
      data: data.map(d => [d[0], '汇报', d[2]]),
      label: { show: false },
      itemStyle: { borderRadius: 2 },
    }],
    grid: { left: 10, right: 10, top: 10, bottom: 10 }
  })
}

onMounted(() => { fetchData(); window.addEventListener('resize', () => { [trendRef, cycleRef, workloadRef, efficiencyRef, excTrendRef, excTypeRef, milestoneRef, heatmapRef].forEach(r => r.value && echarts.getInstanceByDom(r.value)?.resize()) }) })
</script>

<style scoped>
.analytics-dashboard { padding: 16px; }
.filter-bar { margin-bottom: 16px; display: flex; align-items: center; }
.kpi-row { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 16px; }
.kpi-card { background: #fff; border-radius: 8px; padding: 16px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
.kpi-value { font-size: 28px; font-weight: 700; }
.kpi-label { font-size: 13px; color: #909399; margin-top: 4px; }
.chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }
.chart-card { background: #fff; border-radius: 8px; padding: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
.chart-title { font-weight: 600; margin-bottom: 8px; font-size: 14px; }
.chart-box { height: 280px; }
</style>
