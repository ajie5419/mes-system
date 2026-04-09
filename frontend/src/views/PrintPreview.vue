<template>
  <div class="print-overlay-wrapper">
    <div class="print-actions no-print">
      <el-button type="primary" :icon="Printer" @click="doPrint">打印</el-button>
      <el-button @click="$emit('close')">关闭</el-button>
    </div>
    <div v-loading="loading" class="print-page" id="print-area">
      <!-- 页眉 -->
      <div class="print-header">
        <h1>MES 智造管理系统</h1>
        <p>{{ printType === 'work-order' ? '工单详情报告' : '进度汇报报告' }} | 打印日期：{{ formatDate(new Date()) }}</p>
      </div>

      <template v-if="data">
        <!-- 工单基本信息 -->
        <div class="print-section">
          <div class="print-info-grid">
            <div class="print-info-item"><span class="label">工单号：</span><span class="value">{{ data.work_order.wo_number }}</span></div>
            <div class="print-info-item"><span class="label">项目名称：</span><span class="value">{{ data.work_order.project_name }}</span></div>
            <div class="print-info-item"><span class="label">客户：</span><span class="value">{{ data.work_order.customer_name || '-' }}</span></div>
            <div class="print-info-item"><span class="label">优先级：</span><span class="value">{{ data.work_order.priority }}</span></div>
            <div class="print-info-item"><span class="label">状态：</span><span class="value">{{ statusLabel(data.work_order.status) }}</span></div>
            <div class="print-info-item"><span class="label">计划交期：</span><span class="value">{{ data.work_order.planned_delivery_date }}</span></div>
            <div class="print-info-item"><span class="label">总进度：</span><span class="value">{{ data.work_order.total_progress?.toFixed(1) }}%</span></div>
            <div class="print-info-item"><span class="label">健康度：</span><span class="value">{{ data.work_order.health_status }}</span></div>
            <div class="print-info-item"><span class="label">当前阶段：</span><span class="value">{{ data.work_order.current_stage }}</span></div>
          </div>
        </div>

        <!-- 里程碑进度表 -->
        <div class="print-section" v-if="data.milestones?.length">
          <div class="print-section-title">里程碑进度</div>
          <table class="print-table">
            <thead>
              <tr>
                <th>节点名称</th>
                <th>计划开始</th>
                <th>计划结束</th>
                <th>实际开始</th>
                <th>实际结束</th>
                <th>完成率</th>
                <th>偏差(天)</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in data.milestones" :key="m.id">
                <td>{{ m.node_name }}</td>
                <td>{{ m.planned_start_date }}</td>
                <td>{{ m.planned_end_date }}</td>
                <td>{{ m.actual_start_date || '-' }}</td>
                <td>{{ m.actual_end_date || '-' }}</td>
                <td>{{ m.completion_rate?.toFixed(1) }}%</td>
                <td>{{ m.deviation_days }}</td>
                <td>{{ milestoneStatusLabel(m.status) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 进度汇报（工单模式用 recent_reports，进度模式用 reports） -->
        <div class="print-section" v-if="displayReports.length">
          <div class="print-section-title">进度汇报记录</div>
          <table class="print-table">
            <thead>
              <tr>
                <th>汇报日期</th>
                <th>里程碑节点</th>
                <th>班组</th>
                <th>汇报人</th>
                <th>完成率</th>
                <th>备注</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in displayReports" :key="r.id">
                <td>{{ r.report_date }}</td>
                <td>{{ r.milestone_name }}</td>
                <td>{{ r.team_name || '-' }}</td>
                <td>{{ r.reported_by || '-' }}</td>
                <td>{{ r.completion_rate?.toFixed(1) }}%</td>
                <td>{{ r.remark || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 变更记录（仅工单模式） -->
        <div class="print-section" v-if="printType === 'work-order' && data.change_records?.length">
          <div class="print-section-title">变更记录</div>
          <table class="print-table">
            <thead>
              <tr>
                <th>变更类型</th>
                <th>描述</th>
                <th>发起人</th>
                <th>状态</th>
                <th>发起时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in data.change_records" :key="c.id">
                <td>{{ c.change_type }}</td>
                <td>{{ c.description }}</td>
                <td>{{ c.initiated_by || '-' }}</td>
                <td>{{ changeStatusLabel(c.status) }}</td>
                <td>{{ c.created_at?.substring(0, 10) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 质量问题（仅工单模式） -->
        <div class="print-section" v-if="printType === 'work-order' && data.quality_issues?.length">
          <div class="print-section-title">质量问题记录</div>
          <table class="print-table">
            <thead>
              <tr>
                <th>问题类型</th>
                <th>描述</th>
                <th>状态</th>
                <th>记录时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="qi in data.quality_issues" :key="qi.id">
                <td>{{ qi.issue_type }}</td>
                <td>{{ qi.description }}</td>
                <td>{{ qi.status }}</td>
                <td>{{ qi.created_at?.substring(0, 10) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 页脚 -->
        <div class="print-footer">
          <span>打印人：{{ currentUser }}</span>
          <span style="margin: 0 20px;">|</span>
          <span>打印时间：{{ formatDateTime(new Date()) }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Printer } from '@element-plus/icons-vue'
import { getWorkOrderPrintData, getProgressReportPrintData } from '../api'
import '../styles/print.css'

const props = defineProps<{
  printType: 'work-order' | 'progress-report'
  resourceId: number
}>()

defineEmits<{
  close: []
}>()

const loading = ref(true)
const data = ref<any>(null)

const currentUser = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}')
    return u.display_name || u.username || '-'
  } catch { return '-' }
})

const displayReports = computed(() => {
  if (!data.value) return []
  if (props.printType === 'work-order') return data.value.recent_reports || []
  return data.value.reports || []
})

const statusMap: Record<string, string> = {
  Backlog: '待排产', InProgress: '进行中', Blocked: '已阻塞', Completed: '已完成', Archived: '已归档'
}
const milestoneMap: Record<string, string> = {
  Pending: '待开始', InProgress: '进行中', Completed: '已完成'
}
const changeMap: Record<string, string> = {
  Pending: '待确认', Confirmed: '已确认', Rejected: '已驳回'
}

const statusLabel = (s: string) => statusMap[s] || s
const milestoneStatusLabel = (s: string) => milestoneMap[s] || s
const changeStatusLabel = (s: string) => changeMap[s] || s

function formatDate(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
function formatDateTime(d: Date) {
  return `${formatDate(d)} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function doPrint() {
  window.print()
}

onMounted(async () => {
  try {
    if (props.printType === 'work-order') {
      data.value = await getWorkOrderPrintData(props.resourceId)
    } else {
      data.value = await getProgressReportPrintData(props.resourceId)
    }
  } catch (e: any) {
    console.error('打印数据加载失败', e)
  } finally {
    loading.value = false
  }
})
</script>
