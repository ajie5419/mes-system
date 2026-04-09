<template>
  <div class="page-container">
    <div class="page-header"><h2>审批中心</h2></div>
    <el-tabs v-model="tab">
      <el-tab-pane label="待审批" name="pending">
        <el-table :data="pendingList" v-loading="loading" stripe>
          <el-table-column prop="flow_name" label="审批流" width="150" />
          <el-table-column prop="wo_id" label="工单ID" width="80" />
          <el-table-column prop="department_name" label="审批部门" width="120" />
          <el-table-column prop="step_order" label="步骤" width="60" />
          <el-table-column prop="created_at" label="发起时间" width="180" />
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="success" size="small" @click="openAction(row, 'approve')">通过</el-button>
              <el-button type="danger" size="small" @click="openAction(row, 'reject')">驳回</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="审批流模板" name="flows">
        <div style="margin-bottom:12px;"><el-button type="primary" @click="showFlowDialog = true">新建审批流</el-button></div>
        <el-table :data="flows" stripe>
          <el-table-column prop="flow_name" label="名称" width="150" />
          <el-table-column prop="description" label="描述" />
          <el-table-column label="步骤" width="200">
            <template #default="{ row }">{{ row.steps?.length || 0 }} 步</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showActionDialog" :title="actionType === 'approve' ? '审批通过' : '驳回'" width="400">
      <el-input v-model="actionComment" type="textarea" placeholder="审批意见" :rows="3" />
      <template #footer>
        <el-button @click="showActionDialog = false">取消</el-button>
        <el-button :type="actionType === 'approve' ? 'success' : 'danger'" @click="doAction">确认</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showFlowDialog" title="新建审批流" width="500">
      <el-form :model="flowForm" label-width="80px">
        <el-form-item label="名称"><el-input v-model="flowForm.flow_name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="flowForm.description" type="textarea" /></el-form-item>
        <el-form-item label="审批步骤">
          <div v-for="(s, i) in flowForm.steps" :key="i" style="display:flex;gap:8px;margin-bottom:8px;">
            <el-select v-model="s.department_id" placeholder="部门"><el-option v-for="d in depts" :key="d.id" :label="d.name" :value="d.id" /></el-select>
            <el-input v-model="s.approver_id" placeholder="审批人ID(可选)" style="width:120px;" />
            <el-button text type="danger" @click="flowForm.steps.splice(i, 1)">删除</el-button>
          </div>
          <el-button size="small" @click="flowForm.steps.push({ department_id: null, approver_id: null })">添加步骤</el-button>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="showFlowDialog = false">取消</el-button><el-button type="primary" @click="doCreateFlow">创建</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getPendingApprovals, approveStep, rejectStep, getApprovalFlows, createApprovalFlow, getDepartmentsFlat } from '../api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const tab = ref('pending')
const loading = ref(false)
const pendingList = ref<any[]>([])
const flows = ref<any[]>([])
const depts = ref<any[]>([])
const showActionDialog = ref(false)
const showFlowDialog = ref(false)
const actionType = ref<'approve' | 'reject'>('approve')
const actionComment = ref('')
const actionStepId = ref(0)

const flowForm = reactive({ flow_name: '', description: '', steps: [{ department_id: null as number | null, approver_id: null as number | null }] })

onMounted(async () => {
  await Promise.all([loadPending(), loadFlows(), loadDepts()])
})

async function loadPending() {
  if (!auth.user?.id) return
  loading.value = true
  try { pendingList.value = await getPendingApprovals(auth.user.id) } catch { pendingList.value = [] }
  finally { loading.value = false }
}

async function loadFlows() {
  try { flows.value = await getApprovalFlows() } catch { flows.value = [] }
}

async function loadDepts() {
  try { depts.value = await getDepartmentsFlat() } catch { depts.value = [] }
}

function openAction(row: any, type: 'approve' | 'reject') {
  actionType.value = type
  actionStepId.value = row.step_id
  actionComment.value = ''
  showActionDialog.value = true
}

async function doAction() {
  if (!auth.user?.id) return
  try {
    if (actionType.value === 'approve') await approveStep(actionStepId.value, auth.user.id, actionComment.value)
    else await rejectStep(actionStepId.value, auth.user.id, actionComment.value)
    ElMessage.success('操作成功')
    showActionDialog.value = false
    loadPending()
  } catch (e: any) { ElMessage.error(e.response?.data?.detail || '操作失败') }
}

async function doCreateFlow() {
  if (!flowForm.flow_name || flowForm.steps.length === 0) { ElMessage.warning('请填写名称和步骤'); return }
  try {
    await createApprovalFlow(flowForm)
    ElMessage.success('创建成功')
    showFlowDialog.value = false
    Object.assign(flowForm, { flow_name: '', description: '', steps: [{ department_id: null, approver_id: null }] })
    loadFlows()
  } catch { ElMessage.error('创建失败') }
}
</script>
