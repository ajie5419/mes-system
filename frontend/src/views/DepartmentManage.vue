<template>
  <div class="page-container">
    <div class="page-header">
      <h2>部门管理</h2>
      <el-button type="primary" @click="showAddDialog()">新增部门</el-button>
    </div>

    <el-table :data="flatList" row-key="id" border default-expand-all :tree-props="{children: 'children'}">
      <el-table-column prop="name" label="部门名称" min-width="180" />
      <el-table-column prop="code" label="部门编码" width="120" />
      <el-table-column prop="sort_order" label="排序" width="80" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="showEditDialog(row)">编辑</el-button>
          <el-popconfirm title="确定删除？" @confirm="handleDelete(row.id)">
            <template #reference>
              <el-button type="danger" link size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑部门' : '新增部门'" width="420px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="部门名称" />
        </el-form-item>
        <el-form-item label="编码">
          <el-input v-model="form.code" placeholder="如 TECH / PURCH" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="上级部门">
          <el-select v-model="form.parent_id" placeholder="无（顶级部门）" clearable style="width:100%">
            <el-option v-for="d in flatList.filter(x => x.id !== form.id)" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="saving">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import client from '../api'

const flatList = ref<any[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const form = ref({ id: 0, name: '', code: '', parent_id: null as number | null, sort_order: 0 })

async function loadDepartments() {
  try {
    const { data } = await client.get('/departments/')
    flatList.value = data || []
  } catch { ElMessage.error('加载部门失败') }
}

function showAddDialog() {
  isEdit.value = false
  form.value = { id: 0, name: '', code: '', parent_id: null, sort_order: 0 }
  dialogVisible.value = true
}

function showEditDialog(row: any) {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.name || !form.value.code) { ElMessage.warning('请填写完整'); return }
  saving.value = true
  try {
    if (isEdit.value) {
      await client.put(`/departments/${form.value.id}`, form.value)
      ElMessage.success('更新成功')
    } else {
      await client.post('/departments/', form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadDepartments()
  } catch { ElMessage.error('操作失败') }
  finally { saving.value = false }
}

async function handleDelete(id: number) {
  try {
    await client.delete(`/departments/${id}`)
    ElMessage.success('删除成功')
    loadDepartments()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

onMounted(loadDepartments)
</script>
