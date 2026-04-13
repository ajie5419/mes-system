<template>
  <div class="page-container">
    <div class="page-header"><h2>异常管理中心</h2><el-button type="primary" @click="showCreateDialog = true">上报异常</el-button></div>

    <!-- 统计卡片 -->
    <div class="stats-row" v-loading="statsLoading">
      <div class="stat-card"><div class="stat-num">{{ stats.total }}</div><div class="stat-label">总数</div></div>
      <div class="stat-card warn"><div class="stat-num">{{ stats.open }}</div><div class="stat-label">待处理</div></div>
      <div class="stat-card info"><div class="stat-num">{{ stats.in_progress }}</div><div class="stat-label">处理中</div></div>
      <div class="stat-card ok"><div class="stat-num">{{ stats.resolved }}</div><div class="stat-label">已解决</div></div>
      <div class="stat-card"><div class="stat-num">{{ stats.avg_resolve_hours }}h</div><div class="stat-label">平均解决</div></div>
    </div>

    <!-- 趋势图 -->
    <div style="margin:16px 0;">
      <v-chart :option="trendOption" style="height:280px;" autoresize />
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-select v-model="filters.exception_type" placeholder="类型" clearable style="width:140px;" @change="loadList">
        <el-option v-for="t in exceptionTypes" :key="t" :label="t" :value="t" />
      </el-select>
      <el-select v-model="filters.severity" placeholder="严重度" clearable style="width:120px;" @change="loadList">
        <el-option v-for="t in severities" :key="t" :label="t" :value="t" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable style="width:120px;" @change="loadList">
        <el-option v-for="t in statuses" :key="t" :label="statusLabel(t)" :value="t" />
      </el-select>
    </div>

    <!-- 列表 -->
    <el-table :data="list" v-loading="listLoading" stripe>
      <el-table-column prop="exception_type" label="类型" width="100" />
      <el-table-column prop="severity" label="严重度" width="80">
        <template #default="{ row }"><el-tag :type="sevType(row.severity)" size="small">{{ statusText(row.severity) }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="department_name" label="部门" width="100" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }"><el-tag size="small" :type="row.status === 'resolved' ? 'success' : row.status === 'open' ? 'danger' : 'warning'">{{ statusLabel(row.status) }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="created_at" label="上报时间" width="170" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button text size="small" @click="openDetail(row)">详情</el-button>
          <el-button text size="small" type="warning" @click="handleEscalate(row.id)" v-if="row.status !== 'resolved'">升级</el-button>
          <el-button text size="small" type="success" @click="openResolve(row.id)" v-if="row.status !== 'resolved'">解决</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar"><el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="total, prev, pager, next" @current-change="loadList" /></div>

    <!-- 上报弹窗 -->
    <el-dialog v-model="showCreateDialog" title="上报异常" width="500">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="类型"><el-select v-model="createForm.exception_type"><el-option v-for="t in exceptionTypes" :key="t" :label="t" :value="t" /></el-select></el-form-item>
        <el-form-item label="严重度"><el-select v-model="createForm.severity"><el-option v-for="t in severities" :key="t" :label="t" :value="t" /></el-select></el-form-item>
        <el-form-item label="描述"><el-input v-model="createForm.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="部门"><el-select v-model="createForm.department_id"><el-option v-for="d in depts" :key="d.id" :label="d.name" :value="d.id" /></el-select></el-form-item>
        <el-form-item label="工单ID"><el-input-number v-model="createForm.wo_id" :min="1" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showCreateDialog = false">取消</el-button><el-button type="primary" @click="doCreate">上报</el-button></template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="showDetailDialog" title="异常详情" width="600">
      <el-descriptions v-if="detail" :column="2" border>
        <el-descriptions-item label="类型">{{ detail.exception_type }}</el-descriptions-item>
        <el-descriptions-item label="严重度"><el-tag :type="sevType(detail.severity)">{{ statusText(detail.severity) }}</el-tag></el-descriptions-item>
        <el-descriptions-item label="部门">{{ detail.department_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ statusLabel(detail.status) }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ detail.description }}</el-descriptions-item>
        <el-descriptions-item label="原因分析" :span="2">{{ detail.root_cause || '—' }}</el-descriptions-item>
        <el-descriptions-item label="解决方案" :span="2">{{ detail.solution || '—' }}</el-descriptions-item>
        <el-descriptions-item label="上报时间">{{ detail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="解决时间">{{ detail.resolved_at || '—' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 解决弹窗 -->
    <el-dialog v-model="showResolveDialog" title="解决异常" width="500">
      <el-form :model="resolveForm" label-width="80px">
        <el-form-item label="原因分析"><el-input v-model="resolveForm.root_cause" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="解决方案"><el-input v-model="resolveForm.solution" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showResolveDialog = false">取消</el-button><el-button type="primary" @click="doResolve">确认解决</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { statusText } from '../utils/constants'
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { getExceptions, getExceptionStats, createException, escalateException, resolveException, getException, getDepartmentsFlat } from '../api'
import { useAuthStore } from '../stores/auth'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])
const auth = useAuthStore()

const exceptionTypes = ['物料短缺', '设备故障', '人员不足', '质量异常', '交期异常', '其他']
const severities = ['low', 'medium', 'high', 'critical']
const statuses = ['open', 'in_progress', 'resolved', 'closed']
const statusLabel = (s: string) => ({ open: '待处理', in_progress: '处理中', resolved: '已解决', closed: '已关闭' } as any)[s] || s
const sevType = (s: string) => ({ low: 'info', medium: 'warning', high: 'danger', critical: 'danger' } as any)[s] || 'info'

const stats = ref<any>({})
const list = ref<any[]>([])
const depts = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const statsLoading = ref(false)
const listLoading = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showResolveDialog = ref(false)
const detail = ref<any>(null)
const resolveId = ref(0)

const filters = reactive({ exception_type: '', severity: '', status: '' })
const createForm = reactive({ exception_type: '物料短缺', severity: 'medium', description: '', department_id: null as number | null, wo_id: null as number | null })
const resolveForm = reactive({ root_cause: '', solution: '' })

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: (stats.value.trend || []).map((t: any) => t.date) },
  yAxis: { type: 'value', minInterval: 1 },
  series: [{ type: 'line', data: (stats.value.trend || []).map((t: any) => t.count), smooth: true, areaStyle: { opacity: 0.3 } }],
  grid: { left: 40, right: 20, bottom: 30, top: 20 },
}))

onMounted(async () => {
  await Promise.all([loadStats(), loadList(), loadDepts()])
})

async function loadStats() {
  statsLoading.value = true
  try { stats.value = await getExceptionStats() } catch {}
  finally { statsLoading.value = false }
}

async function loadList() {
  listLoading.value = true
  try {
    const res = await getExceptions({ ...filters, page: page.value })
    list.value = res.items || []; total.value = res.total || 0
  } catch { list.value = [] }
  finally { listLoading.value = false }
}

async function loadDepts() {
  try { depts.value = await getDepartmentsFlat() } catch { depts.value = [] }
}

async function doCreate() {
  if (!createForm.description || !createForm.department_id) { ElMessage.warning('请填写描述和部门'); return }
  try {
    await createException({ ...createForm, reporter_id: auth.user?.id })
    ElMessage.success('上报成功')
    showCreateDialog.value = false
    Object.assign(createForm, { exception_type: '物料短缺', severity: 'medium', description: '', department_id: null, wo_id: null })
    loadList(); loadStats()
  } catch { ElMessage.error('上报失败') }
}

async function openDetail(row: any) {
  try { detail.value = await getException(row.id); showDetailDialog.value = true } catch { ElMessage.error('获取详情失败') }
}

async function handleEscalate(id: number) {
  await ElMessageBox.confirm('确认升级此异常？', '提示', { type: 'warning' })
  try { await escalateException(id); ElMessage.success('已升级'); loadList(); loadStats() } catch { ElMessage.error('升级失败') }
}

function openResolve(id: number) { resolveId.value = id; resolveForm.root_cause = ''; resolveForm.solution = ''; showResolveDialog.value = true }

async function doResolve() {
  if (!resolveForm.root_cause || !resolveForm.solution) { ElMessage.warning('请填写原因分析和解决方案'); return }
  try {
    await resolveException(resolveId.value, resolveForm)
    ElMessage.success('已解决'); showResolveDialog.value = false; loadList(); loadStats()
  } catch { ElMessage.error('操作失败') }
}
</script>

<style scoped>
.stats-row { display: flex; gap: 12px; margin-bottom: 16px; }
.stat-card { flex: 1; background: #f5f7fa; border-radius: 8px; padding: 16px; text-align: center; }
.stat-card.warn { background: #fff7e6; }
.stat-card.info { background: #e6f7ff; }
.stat-card.ok { background: #f6ffed; }
.stat-num { font-size: 28px; font-weight: 700; color: #1a1a1a; }
.stat-label { font-size: 13px; color: #999; margin-top: 4px; }
.filter-bar { display: flex; gap: 8px; margin-bottom: 12px; }
</style>
