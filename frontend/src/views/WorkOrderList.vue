<template>
  <div class="bg-white p-6 rounded-xl shadow-sm border border-f0f0f0">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-lg font-bold text-gray-800">工单府库 (实时调度)</h2>
      <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">新建生产任务</el-button>
    </div>

    <el-table :data="workOrders" stripe v-loading="loading" class="mb-4">
      <el-table-column prop="wo_number" label="工单号" width="160" />
      <el-table-column prop="project_name" label="项目名称" />
      <el-table-column label="状态" width="120">
        <template #default="scope">
          <el-tag :type="scope.row.is_locked ? 'danger' : 'success'" effect="dark">
            {{ scope.row.is_locked ? '已锁定 (变更中)' : scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="健康度" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.health_status === 'RED' ? 'danger' : (scope.row.health_status === 'YELLOW' ? 'warning' : 'success')">
            {{ scope.row.health_status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="scope">
          <el-button size="small" type="primary" @click="openProgressDialog(scope.row)" :disabled="scope.row.is_locked">汇报</el-button>
          <el-button size="small" type="warning" @click="openChangeDialog(scope.row)" :disabled="scope.row.is_locked">发起变更</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 弹窗：新建工单 -->
    <el-dialog v-model="showCreateDialog" title="新建生产任务" width="500px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="项目名称"><el-input v-model="createForm.project_name" placeholder="输入项目全称" /></el-form-item>
        <el-form-item label="客户名称"><el-input v-model="createForm.customer_name" /></el-form-item>
        <el-form-item label="交期节点"><el-date-picker v-model="createForm.planned_delivery_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">钦点下发</el-button>
      </template>
    </el-dialog>

    <!-- 弹窗：汇报进度 -->
    <el-dialog v-model="showProgressDialog" title="提交进度汇报" width="400px">
      <el-form :model="progressForm" label-width="100px">
        <el-form-item label="汇报节点">
          <el-select v-model="progressForm.milestone_id" placeholder="选择当前节点">
             <el-option v-for="m in currentWoMilestones" :key="m.id" :label="m.node_name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="完成比例"><el-input-number v-model="progressForm.completion_rate" :min="0" :max="100" /> %</el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="handleReport">提交进度</el-button>
      </template>
    </el-dialog>

    <!-- 弹窗：发起变更 -->
    <el-dialog v-model="showChangeDialog" title="发起变更申请" width="500px">
      <el-form :model="changeForm" label-width="100px">
        <el-form-item label="变更类型">
          <el-select v-model="changeForm.change_type">
            <el-option label="技术变更" value="技术变更" />
            <el-option label="工艺变更" value="工艺变更" />
            <el-option label="计划变更" value="计划变更" />
          </el-select>
        </el-form-item>
        <el-form-item label="变更描述"><el-input type="textarea" v-model="changeForm.description" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button type="warning" @click="handleChange">锁定并下发通知</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { getWorkOrders, createWorkOrder, reportProgress, createChange, client } from '../api'
import { ElMessage } from 'element-plus'

const workOrders = ref([])
const loading = ref(false)

// 新建
const showCreateDialog = ref(false)
const createForm = ref({ project_name: '', customer_name: '', planned_delivery_date: '' })

// 汇报
const showProgressDialog = ref(false)
const currentWoMilestones = ref([])
const progressForm = ref({ wo_id: 0, milestone_id: '', completion_rate: 0, report_date: '2026-04-09' })

// 变更
const showChangeDialog = ref(false)
const changeForm = ref({ wo_id: 0, change_type: '技术变更', description: '', notify_departments: ['生产部', '采购部', '项目部'] })

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getWorkOrders({ page_size: 50 })
    workOrders.value = res.items
  } finally { loading.value = false }
}

const handleCreate = async () => {
  await createWorkOrder(createForm.value)
  ElMessage.success('工单下发成功')
  showCreateDialog.value = false
  fetchData()
}

const openProgressDialog = async (row) => {
  progressForm.value.wo_id = row.id
  const detail = await (await fetch(`http://localhost:8000/api/v1/work-orders/${row.id}`)).json()
  currentWoMilestones.value = detail.milestones
  showProgressDialog.value = true
}

const handleReport = async () => {
  try {
    await reportProgress(progressForm.value)
    ElMessage.success('进度汇报已入库')
    showProgressDialog.value = false
    fetchData()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '汇报失败')
  }
}

const openChangeDialog = (row) => {
  changeForm.value.wo_id = row.id
  showChangeDialog.value = true
}

const handleChange = async () => {
  await createChange(changeForm.value)
  ElMessage.warning('变更已发起，工单已锁定')
  showChangeDialog.value = false
  fetchData()
}

onMounted(fetchData)
</script>
