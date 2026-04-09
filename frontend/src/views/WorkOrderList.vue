<template>
  <div class="page-container">
    <div class="page-header">
      <h2>工单府库</h2>
      <ExportButton export-type="work-orders" :params="filters" />
        <el-button v-permission="'work_orders:create'" type="primary" :icon="Plus" @click="openCreateDialog">新建生产任务</el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-input v-model="filters.keyword" placeholder="搜索工单号 / 项目名" clearable style="width:220px" @keyup.enter="fetchData" />
      <el-select v-model="filters.status" placeholder="状态" clearable style="width:140px" @change="fetchData">
        <el-option v-for="s in statusOptions" :key="s" :label="s" :value="s" />
      </el-select>
      <el-select v-model="filters.is_delayed" placeholder="延期" clearable style="width:100px" @change="fetchData">
        <el-option label="是" :value="true" />
        <el-option label="否" :value="false" />
      </el-select>
      <el-button type="primary" plain @click="fetchData">查询</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="workOrders" v-loading="loading" stripe @sort-change="handleSort" row-key="id">
      <el-table-column prop="wo_number" label="工单号" width="150" sortable="custom">
        <template #default="{ row }">
          <el-link type="primary" @click="goDetail(row)">{{ row.wo_number }}</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="project_name" label="项目名称" min-width="160" show-overflow-tooltip />
      <el-table-column prop="customer_name" label="客户" width="120" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="110" sortable="custom">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small" effect="light">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="health_status" label="健康度" width="90" sortable="custom">
        <template #default="{ row }">
          <el-tag :type="healthTagType(row.health_status)" size="small" round>{{ healthLabel(row.health_status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="planned_delivery_date" label="计划交期" width="120" sortable="custom">
        <template #default="{ row }">{{ fmtDate(row.planned_delivery_date) }}</template>
      </el-table-column>
      <el-table-column prop="overall_progress" label="总进度" width="140">
        <template #default="{ row }">
          <el-progress :percentage="row.overall_progress || 0" :stroke-width="8" :color="progressColor(row.overall_progress)" />
        </template>
      </el-table-column>
      <el-table-column label="锁定" width="70" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_locked" type="danger" size="small" effect="dark">是</el-tag>
          <span v-else style="color:#ccc">—</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button v-permission="'progress:report'" size="small" type="primary" link @click="openProgressDialog(row)" :disabled="row.is_locked">汇报进度</el-button>
          <el-button size="small" type="warning" link @click="openChangeDialog(row)" :disabled="row.is_locked">发起变更</el-button>
          <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination background layout="total, sizes, prev, pager, next"
        :total="total" v-model:page-size="pageSize" v-model:current-page="currentPage"
        :page-sizes="[10, 20, 50]" @current-change="fetchData" @size-change="fetchData" />
    </div>

    <!-- 新建工单 -->
    <el-dialog v-model="showCreateDialog" title="新建生产任务" width="520px" destroy-on-close>
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="100px">
        <el-form-item label="项目名称" prop="project_name">
          <el-input v-model="createForm.project_name" placeholder="输入项目全称" />
        </el-form-item>
        <el-form-item label="客户名称" prop="customer_name">
          <el-input v-model="createForm.customer_name" />
        </el-form-item>
        <el-form-item label="计划交期" prop="planned_delivery_date">
          <el-date-picker v-model="createForm.planned_delivery_date" type="date" value-format="YYYY-MM-DD" placeholder="选择交期" style="width:100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="submitting">确认下发</el-button>
      </template>
    </el-dialog>

    <!-- 进度汇报 -->
    <el-dialog v-model="showProgressDialog" title="提交进度汇报" width="480px" destroy-on-close>
      <el-form ref="progressFormRef" :model="progressForm" :rules="progressRules" label-width="100px">
        <el-form-item label="汇报节点" prop="milestone_id">
          <el-select v-model="progressForm.milestone_id" placeholder="选择当前节点" style="width:100%">
            <el-option v-for="m in currentWoMilestones" :key="m.id" :label="m.node_name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="完成比例" prop="completion_rate">
          <el-slider v-model="progressForm.completion_rate" :min="0" :max="100" show-input />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showProgressDialog = false">取消</el-button>
        <el-button type="primary" @click="handleReport" :loading="submitting">提交</el-button>
      </template>
    </el-dialog>

    <!-- 发起变更 -->
    <el-dialog v-model="showChangeDialog" title="发起变更申请" width="520px" destroy-on-close>
      <el-form ref="changeFormRef" :model="changeForm" :rules="changeRules" label-width="100px">
        <el-form-item label="变更类型" prop="change_type">
          <el-select v-model="changeForm.change_type" style="width:100%">
            <el-option label="技术变更" value="技术变更" />
            <el-option label="工艺变更" value="工艺变更" />
            <el-option label="计划变更" value="计划变更" />
          </el-select>
        </el-form-item>
        <el-form-item label="变更描述" prop="description">
          <el-input type="textarea" v-model="changeForm.description" :rows="4" placeholder="描述变更内容" />
        </el-form-item>
        <el-form-item label="通知部门">
          <el-checkbox-group v-model="changeForm.notify_departments">
            <el-checkbox label="生产部" />
            <el-checkbox label="采购部" />
            <el-checkbox label="项目管理部" />
            <el-checkbox label="技术部" />
            <el-checkbox label="工艺部" />
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showChangeDialog = false">取消</el-button>
        <el-button type="warning" @click="handleChange" :loading="submitting">锁定并下发</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import ExportButton from '../components/ExportButton.vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getWorkOrders, createWorkOrder, getWorkOrder, reportProgress, createChange, deleteWorkOrder } from '../api'

const emit = defineEmits<{ (e: 'navigate', p: { id: string; name: string }): void }>()

const workOrders = ref<any[]>([])
const loading = ref(false)
const submitting = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const sortField = ref('')
const sortOrder = ref('')

const filters = reactive({ keyword: '', status: '', is_delayed: undefined as boolean | undefined })
const statusOptions = ['Backlog', 'InProgress', 'Blocked', 'Completed', 'Archived']

const today = () => new Date().toISOString().slice(0, 10)

// ── 新建 ──
const showCreateDialog = ref(false)
const createFormRef = ref<FormInstance>()
const createForm = reactive({ project_name: '', customer_name: '', planned_delivery_date: '' })
const createRules: FormRules = {
  project_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  customer_name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  planned_delivery_date: [{ required: true, message: '请选择计划交期', trigger: 'change' }],
}

// ── 进度 ──
const showProgressDialog = ref(false)
const progressFormRef = ref<FormInstance>()
const currentWoMilestones = ref<any[]>([])
const progressForm = reactive({ wo_id: 0, milestone_id: '' as any, completion_rate: 0 })
const progressRules: FormRules = {
  milestone_id: [{ required: true, message: '请选择节点', trigger: 'change' }],
}

// ── 变更 ──
const showChangeDialog = ref(false)
const changeFormRef = ref<FormInstance>()
const changeForm = reactive({ wo_id: 0, change_type: '技术变更', description: '', notify_departments: ['生产部', '采购部', '项目管理部'] })
const changeRules: FormRules = {
  change_type: [{ required: true, message: '请选择变更类型', trigger: 'change' }],
  description: [{ required: true, message: '请输入变更描述', trigger: 'blur' }],
}

// ── 数据 ──
const fetchData = async () => {
  loading.value = true
  try {
    const params: any = { page: currentPage.value, page_size: pageSize.value }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.status) params.status = filters.status
    if (filters.is_delayed !== undefined) params.is_delayed = filters.is_delayed
    const res = await getWorkOrders(params)
    workOrders.value = res.items || []
    total.value = res.total || 0
  } catch (e: any) { ElMessage.error(e?.response?.data?.detail || '加载失败') }
  finally { loading.value = false }
}

const handleSort = ({ prop, order }: any) => {
  sortField.value = prop || ''
  sortOrder.value = order === 'ascending' ? 'asc' : order === 'descending' ? 'desc' : ''
  fetchData()
}

const handleCreate = async () => {
  await createFormRef.value?.validate()
  submitting.value = true
  try {
    await createWorkOrder(createForm)
    ElMessage.success('工单下发成功')
    showCreateDialog.value = false
    Object.assign(createForm, { project_name: '', customer_name: '', planned_delivery_date: '' })
    fetchData()
  } catch (e: any) { ElMessage.error(e?.response?.data?.detail || '创建失败') }
  finally { submitting.value = false }
}

const openCreateDialog = () => { showCreateDialog.value = true }

const openProgressDialog = async (row: any) => {
  progressForm.wo_id = row.id
  progressForm.milestone_id = ''
  progressForm.completion_rate = 0
  try {
    const detail = await getWorkOrder(row.id)
    currentWoMilestones.value = detail.milestones || []
  } catch { currentWoMilestones.value = [] }
  showProgressDialog.value = true
}

const handleReport = async () => {
  await progressFormRef.value?.validate()
  submitting.value = true
  try {
    await reportProgress({ ...progressForm, report_date: today() })
    ElMessage.success('进度已入库')
    showProgressDialog.value = false
    fetchData()
  } catch (e: any) { ElMessage.error(e?.response?.data?.detail || '汇报失败') }
  finally { submitting.value = false }
}

const openChangeDialog = (row: any) => {
  changeForm.wo_id = row.id
  changeForm.change_type = '技术变更'
  changeForm.description = ''
  showChangeDialog.value = true
}

const handleChange = async () => {
  await changeFormRef.value?.validate()
  submitting.value = true
  try {
    await createChange(changeForm)
    ElMessage.warning('变更已发起，工单已锁定')
    showChangeDialog.value = false
    fetchData()
  } catch (e: any) { ElMessage.error(e?.response?.data?.detail || '变更失败') }
  finally { submitting.value = false }
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除工单 ${row.wo_number}？此操作不可恢复。`, '危险操作', { type: 'error', confirmButtonText: '确认删除', cancelButtonText: '取消' })
  try {
    await deleteWorkOrder(row.id)
    ElMessage.success('已删除')
    fetchData()
  } catch (e: any) { ElMessage.error(e?.response?.data?.detail || '删除失败') }
}

const goDetail = (row: any) => {
  emit('navigate', { id: `wo-detail-${row.id}`, name: `工单 ${row.wo_number}`, woId: row.id })
}

// ── 格式化工具 ──
const fmtDate = (d: string) => d ? d.slice(0, 10) : '—'
const statusTagType = (s: string) => ({ Backlog: 'info', InProgress: 'primary', Blocked: 'danger', Completed: 'success', Archived: 'info' }[s] || 'info')
const healthTagType = (h: string) => ({ GREEN: 'success', YELLOW: 'warning', RED: 'danger' }[h] || 'info')
const healthLabel = (h: string) => ({ GREEN: '正常', YELLOW: '预警', RED: '延期' }[h] || h)
const progressColor = (p: number) => p >= 80 ? '#52c41a' : p >= 50 ? '#1890ff' : p >= 30 ? '#faad14' : '#ff4d4f'

onMounted(fetchData)
</script>

<style scoped>
.filter-bar { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; align-items: center; }
</style>
