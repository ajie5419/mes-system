<template>
  <div class="page-container">
    <div class="page-header">
      <h2>供应商名录</h2>
      <el-button type="primary" :icon="Plus" @click="openDialog(null)">新增供应商</el-button>
    </div>

    <el-table :data="suppliers" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="商号" min-width="160" />
      <el-table-column prop="contact" label="联络方式" width="180" show-overflow-tooltip />
      <el-table-column prop="rating" label="信用评级" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="ratingType(row.rating)" size="small" round>{{ row.rating || '未评' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="openDialog(row)">编辑</el-button>
          <el-button size="small" type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>

  <el-dialog v-model="showDialog" :title="editingId ? '编辑供应商' : '新增供应商'" width="440px" destroy-on-close>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="商号" prop="name">
        <el-input v-model="form.name" placeholder="供应商名称" />
      </el-form-item>
      <el-form-item label="联络方式" prop="contact">
        <el-input v-model="form.contact" placeholder="电话 / 邮箱" />
      </el-form-item>
      <el-form-item label="信用评级" prop="rating">
        <el-radio-group v-model="form.rating">
          <el-radio-button label="A" />
          <el-radio-button label="B" />
          <el-radio-button label="C" />
          <el-radio-button label="D" />
        </el-radio-group>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showDialog = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitting">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSuppliers, createSupplier, updateSupplier, deleteSupplier } from '../api'

const suppliers = ref<any[]>([])
const loading = ref(false)
const submitting = ref(false)

const showDialog = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const form = ref({ name: '', contact: '', rating: 'C' })
const rules: FormRules = {
  name: [{ required: true, message: '请输入商号', trigger: 'blur' }],
}

const fetchData = async () => {
  loading.value = true
  try { suppliers.value = await getSuppliers() }
  catch { suppliers.value = [] }
  finally { loading.value = false }
}

const openDialog = (row: any | null) => {
  editingId.value = row?.id || null
  form.value = { name: row?.name || '', contact: row?.contact || '', rating: row?.rating || 'C' }
  showDialog.value = true
}

const handleSubmit = async () => {
  await formRef.value?.validate()
  submitting.value = true
  try {
    if (editingId.value) {
      await updateSupplier(editingId.value, form.value)
      ElMessage.success('已更新')
    } else {
      await createSupplier(form.value)
      ElMessage.success('已入库')
    }
    showDialog.value = false
    fetchData()
  } catch (e: any) { ElMessage.error(e?.response?.data?.detail || '操作失败') }
  finally { submitting.value = false }
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除「${row.name}」？`, '确认', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' })
  try {
    await deleteSupplier(row.id)
    ElMessage.success('已删除')
    fetchData()
  } catch (e: any) { ElMessage.error(e?.response?.data?.detail || '删除失败') }
}

const ratingType = (r: string) => ({ A: 'success', B: 'primary', C: 'warning', D: 'danger' }[r] || 'info')

onMounted(fetchData)
</script>
