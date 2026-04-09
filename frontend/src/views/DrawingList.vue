<template>
  <div class="bg-white p-6 rounded-xl shadow-sm border border-f0f0f0">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-lg font-bold">图纸百宝库</h2>
      <el-button type="primary" @click="dialogVisible = true">上传图纸</el-button>
    </div>

    <el-table :data="drawings" border stripe>
      <el-table-column prop="wo_id" label="所属工单" width="120" />
      <el-table-column prop="version" label="版本号" width="100" />
      <el-table-column label="文件名" min-width="200">
        <template #default="{ row }">
          <el-link v-if="row.file_url" type="primary" :href="row.file_url" target="_blank">{{ row.file_url.split('/').pop() }}</el-link>
          <span v-else class="text-gray-400">无文件</span>
        </template>
      </el-table-column>
      <el-table-column label="文件大小" width="120">
        <template #default="{ row }">
          {{ row.file_size ? formatSize(row.file_size) : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="入库时间" width="180">
        <template #default="{ row }">{{ fmtDateTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="上传图纸" width="500px" @close="resetForm">
      <el-form :model="form" label-width="80px">
        <el-form-item label="所属工单">
          <el-select v-model="form.wo_id" placeholder="选择工单" filterable style="width:100%">
            <el-option v-for="wo in workOrders" :key="wo.id" :label="`${wo.wo_number} - ${wo.project_name}`" :value="wo.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本号">
          <el-input v-model="form.version" placeholder="V1.0" />
        </el-form-item>
        <el-form-item label="图纸文件">
          <FileUpload :limit="1" @file-selected="onFileSelected" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getDrawings, createDrawingWithFile, getWorkOrders } from '../api'
import FileUpload from '../components/FileUpload.vue'
import { ElMessage } from 'element-plus'

const drawings = ref<any[]>([])
const workOrders = ref<any[]>([])
const dialogVisible = ref(false)
const submitting = ref(false)
const selectedFile = ref<File | null>(null)
const form = ref({ wo_id: null as number | null, version: 'V1.0' })

onMounted(async () => {
  drawings.value = await getDrawings()
  workOrders.value = await getWorkOrders({}) || []
})

function onFileSelected(file: File) {
  selectedFile.value = file
}

function resetForm() {
  form.value = { wo_id: null, version: 'V1.0' }
  selectedFile.value = null
}

async function handleSubmit() {
  if (!form.value.wo_id) return ElMessage.warning('请选择工单')
  submitting.value = true
  try {
    await createDrawingWithFile({
      wo_id: form.value.wo_id,
      version: form.value.version,
      file: selectedFile.value || undefined,
    })
    ElMessage.success('上传成功')
    dialogVisible.value = false
    drawings.value = await getDrawings()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '上传失败')
  } finally {
    submitting.value = false
  }
}

function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function fmtDateTime(s: string) {
  if (!s) return ''
  return s.replace('T', ' ').slice(0, 19)
}
</script>
