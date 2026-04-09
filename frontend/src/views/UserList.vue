<template>
  <div class="page-container">
    <div class="page-header">
      <h2>吏部名册</h2>
      <ExportButton export-type="users" />
      <div class="flex gap-3">
        <el-select v-model="filterDept" placeholder="按部衙筛选" clearable style="width:160px" @change="fetchData">
          <el-option v-for="d in departments" :key="d" :label="d" :value="d" />
        </el-select>
        <el-button type="primary" :icon="Plus" @click="openDialog(null)">新增人员</el-button>
      </div>
    </div>

    <el-table :data="users" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="名讳" width="120" />
      <el-table-column prop="display_name" label="姓名" width="120" />
      <el-table-column prop="department" label="所属部衙" width="130">
        <template #default="{ row }"><el-tag size="small" effect="plain">{{ row.department }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="role" label="职级" width="100">
        <template #default="{ row }">
          <el-tag :type="roleTagType(row.role)" size="small">{{ row.role }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small" round>{{ row.is_active ? '在岗' : '离岗' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="入府日期" width="170">
        <template #default="{ row }">{{ fmtDateTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="openDialog(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>

  <!-- 新增/编辑 -->
  <el-dialog v-model="showDialog" :title="editingId ? '编辑人员' : '新增人员'" width="480px" destroy-on-close>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="名讳" prop="username">
        <el-input v-model="form.username" :disabled="!!editingId" placeholder="登录用户名" />
      </el-form-item>
      <el-form-item label="姓名" prop="display_name">
        <el-input v-model="form.display_name" placeholder="真实姓名" />
      </el-form-item>
      <el-form-item label="所属部衙" prop="department">
        <el-select v-model="form.department" placeholder="选择部门" style="width:100%">
          <el-option v-for="d in departments" :key="d" :label="d" :value="d" />
        </el-select>
      </el-form-item>
      <el-form-item label="职级角色" prop="role">
        <el-select v-model="form.role" placeholder="选择角色" style="width:100%">
          <el-option v-for="r in roles" :key="r" :label="r" :value="r" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="!editingId" label="口令" prop="password">
        <el-input v-model="form.password" type="password" show-password placeholder="设置登录口令" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showDialog = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">{{ editingId ? '保存' : '确认入府' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { getUsers, createUser, updateUser } from '../api'
import ExportButton from '../components/ExportButton.vue'

const departments = ['技术部', '工艺部', '采购部', '生产部', '项目管理部']
const roles = ['Admin', 'Manager', 'Worker']

const users = ref<any[]>([])
const loading = ref(false)
const submitting = ref(false)
const filterDept = ref('')

const showDialog = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const form = ref({ username: '', display_name: '', department: '', role: 'Worker', password: '' })
const rules: FormRules = {
  username: [{ required: true, message: '请输入名讳', trigger: 'blur' }],
  display_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  department: [{ required: true, message: '请选择部门', trigger: 'change' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

const fetchData = async () => {
  loading.value = true
  try { users.value = await getUsers(filterDept.value || undefined) }
  catch { users.value = [] }
  finally { loading.value = false }
}

const openDialog = (row: any | null) => {
  editingId.value = row?.id || null
  form.value = { username: row?.username || '', display_name: row?.display_name || '', department: row?.department || '', role: row?.role || 'Worker', password: '' }
  showDialog.value = true
}

const handleSubmit = async () => {
  await formRef.value?.validate()
  submitting.value = true
  try {
    if (editingId.value) {
      await updateUser(editingId.value, { display_name: form.value.display_name, department: form.value.department, role: form.value.role })
      ElMessage.success('信息已更新')
    } else {
      await createUser(form.value)
      ElMessage.success('新人已入府')
    }
    showDialog.value = false
    fetchData()
  } catch (e: any) { ElMessage.error(e?.response?.data?.detail || '操作失败') }
  finally { submitting.value = false }
}

const roleTagType = (r: string) => ({ Admin: 'danger', Manager: 'warning', Worker: '' }[r] || 'info')
const fmtDateTime = (d: string) => d ? d.replace('T', ' ').slice(0, 19) : '—'

onMounted(fetchData)
</script>

<style scoped>
.flex { display: flex; }
.gap-3 { gap: 12px; }
</style>
