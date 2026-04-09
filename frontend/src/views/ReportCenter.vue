<template>
  <div class="report-center">
    <h3 style="margin-bottom:16px;">报表中心</h3>
    <div class="report-grid">
      <div class="report-card" v-for="r in reports" :key="r.key">
        <div class="report-icon">{{ r.icon }}</div>
        <div class="report-info">
          <div class="report-name">{{ r.name }}</div>
          <div class="report-desc">{{ r.desc }}</div>
          <div class="report-time" v-if="r.lastTime">上次生成：{{ r.lastTime }}</div>
        </div>
        <div class="report-actions">
          <el-button size="small" type="primary" @click="previewReport(r)">预览</el-button>
          <el-button size="small" @click="exportReport(r)">导出</el-button>
        </div>
      </div>
    </div>

    <!-- 预览弹窗 -->
    <el-dialog v-model="previewVisible" :title="previewTitle" width="900px" destroy-on-close>
      <div ref="previewChartRef" style="height:400px;"></div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getAnalyticsKPI, getWOTrend, getExceptionByType, getDeptWorkload, getMilestoneCompletion } from '../api'
import { ElMessage } from 'element-plus'

const previewVisible = ref(false)
const previewTitle = ref('')
const previewChartRef = ref<HTMLElement>()

const reports = ref([
  { key: 'weekly', name: '周报', icon: '📅', desc: '本周工单概览 + 完成情况 + 异常汇总', lastTime: '' },
  { key: 'monthly', name: '月报', icon: '📊', desc: '月度KPI + 趋势分析 + 部门绩效', lastTime: '' },
  { key: 'department', name: '部门报表', icon: '🏢', desc: '按部门的工作量 + 效率 + 异常', lastTime: '' },
  { key: 'exception', name: '异常报表', icon: '⚠️', desc: '异常分布 + 解决情况 + 根因分析', lastTime: '' },
])

async function previewReport(r: any) {
  previewTitle.value = r.name + ' 预览'
  previewVisible.value = true
  await nextTick()

  const c = echarts.init(previewChartRef.value!)
  try {
    if (r.key === 'weekly' || r.key === 'monthly') {
      const [kpi, trend] = await Promise.all([getAnalyticsKPI(), getWOTrend({ start_date: '', end_date: '' })])
      c.setOption({
        title: { text: '工单完成趋势' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: trend.map((d: any) => d.date) },
        yAxis: { type: 'value' },
        series: [
          { name: '新增', type: 'line', data: trend.map((d: any) => d.created) },
          { name: '完成', type: 'line', data: trend.map((d: any) => d.completed) },
        ]
      })
    } else if (r.key === 'department') {
      const data = await getDeptWorkload()
      c.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: data.map((d: any) => d.department) },
        yAxis: { type: 'value' },
        series: [
          { name: '进行中', type: 'bar', stack: 'a', data: data.map((d: any) => d.in_progress) },
          { name: '待办', type: 'bar', stack: 'a', data: data.map((d: any) => d.backlog) },
          { name: '已完成', type: 'bar', stack: 'a', data: data.map((d: any) => d.completed) },
        ]
      })
    } else if (r.key === 'exception') {
      const data = await getExceptionByType()
      c.setOption({
        series: [{ type: 'pie', radius: ['40%', '70%'], data: data.map((d: any) => ({ value: d.count, name: d.type })) }]
      })
    }
    r.lastTime = new Date().toLocaleString('zh-CN')
  } catch (e: any) {
    ElMessage.error('加载失败')
  }
}

async function exportReport(r: any) {
  ElMessage.success(`正在生成「${r.name}」...实际导出需后端 Excel 服务支持`)
  r.lastTime = new Date().toLocaleString('zh-CN')
}
</script>

<style scoped>
.report-center { padding: 16px; }
.report-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.report-card { background: #fff; border-radius: 8px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.08); }
.report-icon { font-size: 32px; }
.report-info { flex: 1; }
.report-name { font-weight: 600; font-size: 15px; }
.report-desc { color: #909399; font-size: 13px; margin-top: 4px; }
.report-time { color: #c0c4cc; font-size: 12px; margin-top: 4px; }
.report-actions { display: flex; gap: 8px; }
</style>
