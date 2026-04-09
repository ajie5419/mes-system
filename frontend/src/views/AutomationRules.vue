<template>
  <div class="page-container">
    <div class="page-header">
      <h2>自动化规则</h2>
      <el-button type="primary" @click="openCreateDialog">新建规则</el-button>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="规则列表" name="rules">
        <el-table :data="rules" stripe size="small">
          <el-table-column prop="name" label="规则名称" min-width="180" />
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="trigger_type" label="触发类型" width="140">
            <template #default="{ row }">
              <el-tag size="small">{{ triggerLabels[row.trigger_type] || row.trigger_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="action_type" label="动作类型" width="140">
            <template #default="{ row }">
              <el-tag size="small" type="warning">{{ actionLabels[row.action_type] || row.action_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_enabled" label="状态" width="80">
            <template #default="{ row }">
              <el-switch :model-value="row.is_enabled" @change="handleToggle(row.id)" size="small" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140">
            <template #default="{ row }">
              <el-button text type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
              <el-popconfirm title="确认删除此规则？" @confirm="handleDelete(row.id)">
                <template #reference><el-button text type="danger" size="small">删除</el-button></template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="执行日志" name="logs">
        <el-table :data="logs" stripe size="small">
          <el-table-column prop="rule_name" label="规则名称" width="180" />
          <el-table-column prop="event_type" label="事件类型" width="140" />
          <el-table-column prop="action_type" label="动作" width="120" />
          <el-table-column prop="execution_status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.execution_status === 'success' ? 'success' : 'danger'" size="small">
                {{ row.execution_status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="error_message" label="错误信息" min-width="200" show-overflow-tooltip />
          <el-table-column prop="created_at" label="时间" width="170" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 新建/编辑弹窗 -->
    <el-dialog v-model="showDialog" :title="editingId ? '编辑规则' : '新建规则'" width="600px" destroy-on-close>
      <el-form label-width="100px" :model="form">
        <el-form-item label="规则名称" required>
          <el-input v-model="form.name" placeholder="输入规则名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="规则描述" />
        </el-form-item>
        <el-form-item label="触发类型" required>
          <el-select v-model="form.trigger_type" style="width:100%">
            <el-option v-for="(label, key) in triggerLabels" :key="key" :label="label" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="触发条件">
          <el-input v-model="triggerConditionStr" type="textarea" :rows="3" placeholder='JSON格式，如: {"new_status": "Completed"}' />
        </el-form-item>
        <el-form-item label="动作类型" required>
          <el-select v-model="form.action_type" style="width:100%">
            <el-option v-for="(label, key) in actionLabels" :key="key" :label="label" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="动作参数">
          <el-input v-model="actionParamsStr" type="textarea" :rows="4" placeholder='JSON格式，如: {"title": "通知标题", "content": "通知内容"}' />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAutomationRules, createAutomationRule, updateAutomationRule, deleteAutomationRule, toggleAutomationRule, getAutomationLogs } from '../api'

const activeTab = ref('rules')
const rules = ref<any[]>([])
const logs = ref<any[]>([])
const showDialog = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)

const triggerLabels: Record<string, string> = {
  status_change: '状态变更',
  exception_created: '异常创建',
  due_date_approaching: '交期临近',
  progress_stalled: '进度停滞',
}

const actionLabels: Record<string, string> = {
  send_notification: '发送通知',
  create_task: '创建任务',
  escalate: '升级通知',
  change_status: '变更状态',
  assign_department: '分配部门',
}

const form = reactive({
  name: '', description: '', trigger_type: 'status_change',
  trigger_condition: {}, action_type: 'send_notification',
  action_params: {}, is_enabled: true,
})
const triggerConditionStr = ref('{}')
const actionParamsStr = ref('{}')

onMounted(() => { loadRules(); loadLogs() })

async function loadRules() {
  try { rules.value = await getAutomationRules() } catch { rules.value = [] }
}

async function loadLogs() {
  try { logs.value = await getAutomationLogs() } catch { logs.value = [] }
}

function openCreateDialog() {
  editingId.value = null
  Object.assign(form, { name: '', description: '', trigger_type: 'status_change', trigger_condition: {}, action_type: 'send_notification', action_params: {}, is_enabled: true })
  triggerConditionStr.value = '{}'
  actionParamsStr.value = '{}'
  showDialog.value = true
}

function openEditDialog(row: any) {
  editingId.value = row.id
  Object.assign(form, { name: row.name, description: row.description || '', trigger_type: row.trigger_type, trigger_condition: row.trigger_condition || {}, action_type: row.action_type, action_params: row.action_params || {}, is_enabled: row.is_enabled })
  triggerConditionStr.value = JSON.stringify(row.trigger_condition || {}, null, 2)
  actionParamsStr.value = JSON.stringify(row.action_params || {}, null, 2)
  showDialog.value = true
}

async function handleSave() {
  try {
    form.trigger_condition = JSON.parse(triggerConditionStr.value || '{}')
    form.action_params = JSON.parse(actionParamsStr.value || '{}')
  } catch { ElMessage.error('JSON格式不正确'); return }
  if (!form.name.trim()) { ElMessage.warning('请输入规则名称'); return }
  saving.value = true
  try {
    if (editingId.value) {
      await updateAutomationRule(editingId.value, form)
      ElMessage.success('规则已更新')
    } else {
      await createAutomationRule(form)
      ElMessage.success('规则已创建')
    }
    showDialog.value = false
    await loadRules()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  } finally { saving.value = false }
}

async function handleDelete(id: number) {
  try { await deleteAutomationRule(id); ElMessage.success('已删除'); await loadRules() }
  catch { ElMessage.error('删除失败') }
}

async function handleToggle(id: number) {
  try { await toggleAutomationRule(id); await loadRules() }
  catch { ElMessage.error('操作失败') }
}
</script>
