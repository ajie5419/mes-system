<template>
  <div class="page-container">
    <div class="page-header">
      <h2>任务看板</h2>
      <el-button type="primary" @click="showCreateDialog = true">新建任务</el-button>
    </div>
    <el-tabs v-model="activeDept" type="border-card" @tab-change="onDeptChange">
      <el-tab-pane v-for="d in departments" :key="d.department_id" :label="d.department_name + ' (' + d.total + ')'" :name="String(d.department_id)" />
    </el-tabs>
    <div v-loading="loading" class="kanban">
      <div v-for="col in columns" :key="col.key" class="kanban-column">
        <div class="kanban-col-header" :style="{ background: col.color }">{{ col.label }} ({{ colCount(col.key) }})</div>
        <div class="kanban-col-body"
             @dragover.prevent
             @drop="onDrop($event, col.key)">
          <div v-for="t in colTasks(col.key)" :key="t.id"
               class="task-card" draggable="true"
               :class="'priority-' + t.priority"
               @dragstart="onDragStart($event, t)">
            <div class="task-card-title">{{ t.task_name }}</div>
            <div class="task-card-meta">
              <el-tag size="small" :type="t.status === 'overdue' ? 'danger' : t.status === 'completed' ? 'success' : t.status === 'in_progress' ? 'primary' : 'info'">
                {{ statusLabel(t.status) }}
              </el-tag>
              <span v-if="t.assignee_name" style="font-size:12px;color:#666;">{{ t.assignee_name }}</span>
              <span v-if="t.due_date" style="font-size:12px;color:#999;margin-left:auto;">{{ t.due_date }}</span>
            </div>
            <div class="task-card-actions">
              <el-button text size="small" type="danger" @click="handleDelete(t.id)">删除</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="showCreateDialog" title="新建任务" width="500">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="任务名称"><el-input v-model="createForm.task_name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="createForm.description" type="textarea" /></el-form-item>
        <el-form-item label="工单ID"><el-input-number v-model="createForm.wo_id" /></el-form-item>
        <el-form-item label="优先级">
          <el-rate v-model="createForm.priority" :max="5" show-score />
        </el-form-item>
        <el-form-item label="负责人"><el-select v-model="createForm.assignee_id" clearable placeholder="选择人员"><el-option v-for="u in users" :key="u.id" :label="u.display_name" :value="u.id" /></el-select></el-form-item>
        <el-form-item label="截止日期"><el-date-picker v-model="createForm.due_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="showCreateDialog = false">取消</el-button><el-button type="primary" @click="handleCreate">创建</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTaskBoardOverview, getDepartmentTasks, createTask, deleteTask, moveTask, getUsers } from '../api'

const loading = ref(false)
const departments = ref<any[]>([])
const activeDept = ref('')
const tasks = ref<any[]>([])
const users = ref<any[]>([])
const showCreateDialog = ref(false)
const dragTaskId = ref<number | null>(null)

const createForm = reactive({ task_name: '', description: '', wo_id: 0, priority: 3, assignee_id: null as number | null, due_date: '' as string })

const columns = [
  { key: 'pending', label: '待处理', color: '#909399' },
  { key: 'in_progress', label: '进行中', color: '#1890ff' },
  { key: 'completed', label: '已完成', color: '#52c41a' },
  { key: 'overdue', label: '已超期', color: '#ff4d4f' },
]

const statusLabel = (s: string) => ({ pending: '待处理', in_progress: '进行中', completed: '已完成', overdue: '已超期' } as any)[s] || s
const colTasks = (status: string) => tasks.value.filter(t => t.status === status)
const colCount = (status: string) => colTasks(status).length

onMounted(async () => {
  await Promise.all([loadOverview(), loadUsers()])
})

async function loadOverview() {
  departments.value = await getTaskBoardOverview()
  if (departments.value.length > 0 && !activeDept.value) {
    activeDept.value = String(departments.value[0].department_id)
    await loadTasks()
  }
}

async function loadUsers() {
  try { const res = await getUsers(); users.value = res.items || res || [] } catch {}
}

async function loadTasks() {
  if (!activeDept.value) return
  loading.value = true
  try { tasks.value = await getDepartmentTasks(Number(activeDept.value)) } catch { tasks.value = [] }
  finally { loading.value = false }
}

function onDeptChange() { loadTasks() }

function onDragStart(e: DragEvent, t: any) {
  dragTaskId.value = t.id
  if (e.dataTransfer) e.dataTransfer.setData('text/plain', String(t.id))
}

async function onDrop(e: DragEvent, newStatus: string) {
  const tid = dragTaskId.value
  if (!tid) return
  dragTaskId.value = null
  try { await moveTask(tid, newStatus); loadTasks() } catch { ElMessage.error('移动失败') }
}

async function handleCreate() {
  if (!createForm.task_name || !createForm.wo_id) { ElMessage.warning('请填写任务名称和工单ID'); return }
  try {
    await createTask({ ...createForm, department_id: Number(activeDept.value) })
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    Object.assign(createForm, { task_name: '', description: '', wo_id: 0, priority: 3, assignee_id: null, due_date: '' })
    loadTasks(); loadOverview()
  } catch { ElMessage.error('创建失败') }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
  try { await deleteTask(id); loadTasks(); loadOverview() } catch { ElMessage.error('删除失败') }
}
</script>

<style scoped>
.kanban { display: flex; gap: 12px; margin-top: 16px; overflow-x: auto; min-height: 500px; }
.kanban-column { flex: 1; min-width: 220px; background: #f5f7fa; border-radius: 8px; display: flex; flex-direction: column; }
.kanban-col-header { padding: 10px 14px; border-radius: 8px 8px 0 0; color: #fff; font-weight: 600; font-size: 14px; }
.kanban-col-body { flex: 1; padding: 8px; min-height: 100px; }
.task-card { background: #fff; border-radius: 6px; padding: 12px; margin-bottom: 8px; cursor: grab; border-left: 3px solid #ddd; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.task-card.priority-1 { border-left-color: #ff4d4f; }
.task-card.priority-2 { border-left-color: #faad14; }
.task-card.priority-3 { border-left-color: #1890ff; }
.task-card-title { font-size: 13px; font-weight: 500; margin-bottom: 6px; }
.task-card-meta { display: flex; align-items: center; gap: 6px; }
.task-card-actions { margin-top: 6px; text-align: right; }
</style>
