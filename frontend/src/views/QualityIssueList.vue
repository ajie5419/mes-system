<template>
  <div class="bg-white p-6 rounded-xl shadow-sm border border-f0f0f0">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-lg font-bold text-red-600 italic">不合格品项管理</h2>
      <el-button type="danger" plain @click="showAdd = true">发现缺陷</el-button>
    </div>

    <el-table :data="issues" stripe>
      <el-table-column prop="created_at" label="发现日期" width="160" />
      <el-table-column prop="wo_id" label="关联工单" width="100" />
      <el-table-column prop="issue_type" label="缺陷类型" width="140">
        <template #default="scope">
          <el-tag type="danger">{{ scope.row.issue_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="详情描述" />
      <el-table-column prop="status" label="当前状态" width="100" />
    </el-table>

    <el-dialog v-model="showAdd" title="记录不合格品项" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="工单ID"><el-input v-model="form.wo_id" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.issue_type">
            <el-option label="制造缺陷" value="制造缺陷" />
            <el-option label="原材料缺陷" value="原材料缺陷" />
            <el-option label="设计偏差" value="设计偏差" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input type="textarea" v-model="form.description" /></el-form-item>
      </el-form>
      <template #footer><el-button type="primary" @click="handleAdd">存证</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getQualityIssues, createQualityIssue } from '../api'
import { ElMessage } from 'element-plus'

const issues = ref([])
const showAdd = ref(false)
const form = ref({ wo_id: '', issue_type: '制造缺陷', description: '' })

const fetchData = async () => { issues.value = await getQualityIssues() }
const handleAdd = async () => {
  await createQualityIssue(form.value)
  ElMessage.warning('缺陷已记录，请督促整改')
  showAdd.value = false
  fetchData()
}
onMounted(fetchData)
</script>
