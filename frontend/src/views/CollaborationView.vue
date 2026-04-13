<template>
  <div class="page-container">
    <div class="page-header"><h2>协作面板</h2></div>
    <div class="collab-toolbar">
      <el-select v-model="selectedWoId" placeholder="选择工单" filterable style="width:300px;" @change="loadCollab">
        <el-option v-for="wo in workOrders" :key="wo.id" :label="`${wo.wo_number} - ${wo.project_name}`" :value="wo.id" />
      </el-select>
    </div>
    <div v-if="selectedWoId">
      <el-row :gutter="16">
        <el-col :span="12">
          <h3 style="margin-bottom:12px;">协作人员</h3>
          <el-table :data="assignees" stripe size="small" v-loading="loading">
            <el-table-column prop="department_name" label="部门" width="120" />
            <el-table-column prop="user_name" label="人员" width="120" />
            <el-table-column prop="role_in_wo" label="工单角色" />
          </el-table>
          <div style="margin-top:12px;">
            <el-button type="primary" size="small" @click="showAssignDialog = true">分配人员</el-button>
          </div>
        </el-col>
        <el-col :span="12">
          <h3 style="margin-bottom:12px;">关联任务</h3>
          <el-table :data="woTasks" stripe size="small">
            <el-table-column prop="task_name" label="任务" />
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }"><el-tag size="small">{{ statusText(row.status) }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="assignee_name" label="负责人" width="100" />
          </el-table>
        </el-col>
      </el-row>
    </div>
    <el-empty v-else description="请选择工单查看协作信息" />

    <!-- 分配弹窗 -->
    <el-dialog v-model="showAssignDialog" title="分配部门人员" width="450">
      <el-form :model="assignForm" label-width="80px">
        <el-form-item label="部门">
          <el-select v-model="assignForm.department_id" @change="loadDeptUsers">
            <el-option v-for="d in depts" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="人员">
          <el-select v-model="assignForm.user_ids" multiple>
            <el-option v-for="u in deptUsers" :key="u.id" :label="u.display_name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="assignForm.role_in_wo">
            <el-option v-for="r in roles" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="showAssignDialog = false">取消</el-button><el-button type="primary" @click="doAssign">分配</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { statusText } from '../utils/constants'
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getWorkOrders, getWorkOrderAssignees, assignWorkOrderDept, getDepartmentTasks, getDepartmentsFlat, getUsers } from '../api'

const loading = ref(false)
const selectedWoId = ref<number | null>(null)
const workOrders = ref<any[]>([])
const assignees = ref<any[]>([])
const woTasks = ref<any[]>([])
const showAssignDialog = ref(false)
const depts = ref<any[]>([])
const deptUsers = ref<any[]>([])

const roles = ['技术负责人', '生产负责人', '采购负责人', '质量负责人', '其他']
const assignForm = reactive({ department_id: null as number | null, user_ids: [] as number[], role_in_wo: '技术负责人' })

onMounted(async () => {
  try { const res = await getWorkOrders({ page_size: 100 }); workOrders.value = res.items || [] } catch {}
  try { depts.value = await getDepartmentsFlat() } catch {}
})

async function loadCollab() {
  if (!selectedWoId.value) return
  loading.value = true
  try {
    const [a, t] = await Promise.all([
      getWorkOrderAssignees(selectedWoId.value),
      loadWoTasks()
    ])
    assignees.value = a
  } catch { assignees.value = []; woTasks.value = [] }
  finally { loading.value = false }
}

async function loadWoTasks() {
  if (!selectedWoId.value) return
  try {
    // load all dept tasks and filter by wo_id
    const allDepts = await getDepartmentsFlat()
    let allTasks: any[] = []
    for (const d of allDepts) {
      try {
        const dt = await getDepartmentTasks(d.id)
        allTasks = allTasks.concat(dt)
      } catch {}
    }
    woTasks.value = allTasks.filter((t: any) => t.wo_id === selectedWoId.value)
  } catch { woTasks.value = [] }
}

async function loadDeptUsers() {
  if (!assignForm.department_id) { deptUsers.value = []; return }
  try {
    const dept = depts.value.find((d: any) => d.id === assignForm.department_id)
    const res = await getUsers(dept?.name)
    deptUsers.value = res.items || res || []
  } catch { deptUsers.value = [] }
}

async function doAssign() {
  if (!selectedWoId.value || !assignForm.department_id || assignForm.user_ids.length === 0) {
    ElMessage.warning('请选择部门和人员'); return
  }
  try {
    await assignWorkOrderDept(selectedWoId.value, assignForm)
    ElMessage.success('分配成功')
    showAssignDialog.value = false
    assignForm.user_ids = []
    loadCollab()
  } catch { ElMessage.error('分配失败') }
}
</script>
