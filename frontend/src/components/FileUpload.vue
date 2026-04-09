<template>
  <div>
    <el-upload
      drag
      action=""
      :auto-upload="false"
      :on-change="onFileChange"
      :before-upload="beforeUpload"
      :file-list="fileList"
      :accept="acceptTypes"
      :limit="limit"
      :on-exceed="handleExceed"
      :on-remove="onRemove"
      class="file-upload-drag"
    >
      <el-icon class="el-icon--upload"><Upload /></el-icon>
      <div class="el-upload__text">拖拽文件至此处，或<em>点击上传</em></div>
      <template #tip>
        <div class="el-upload__tip">
          支持 pdf/dwg/dxf/jpg/png/doc/docx/xls/xlsx/zip/rar，单文件不超过 50MB
        </div>
      </template>
    </el-upload>

    <div v-if="uploadedFiles.length" class="mt-3">
      <div class="text-sm text-gray-500 mb-1">已上传文件</div>
      <div v-for="f in uploadedFiles" :key="f.id" class="flex items-center gap-2 py-1 text-sm">
        <el-link type="primary" :href="f.url" target="_blank">{{ f.file_name }}</el-link>
        <span class="text-gray-400">{{ formatSize(f.file_size) }}</span>
        <el-button type="danger" text size="small" @click="$emit('delete', f)">删除</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'

const ALLOWED = ['pdf','dwg','dxf','jpg','png','doc','docx','xls','xlsx','zip','rar']
const MAX_SIZE = 50 * 1024 * 1024
const acceptTypes = ALLOWED.map(t => `.${t}`).join(',')

const props = withDefaults(defineProps<{
  limit?: number
  uploadedFiles?: any[]
}>(), {
  limit: 10,
  uploadedFiles: () => [],
})

const emit = defineEmits<{
  (e: 'file-selected', file: File): void
  (e: 'delete', file: any): void
}>()

const fileList = ref<UploadFile[]>([])

function beforeUpload(file: File) {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!ext || !ALLOWED.includes(ext)) {
    ElMessage.error(`不支持的文件类型: .${ext}`)
    return false
  }
  if (file.size > MAX_SIZE) {
    ElMessage.error('文件超过 50MB 限制')
    return false
  }
  return true
}

function onFileChange(uploadFile: UploadFile) {
  if (uploadFile.raw) {
    if (!beforeUpload(uploadFile.raw)) {
      fileList.value = fileList.value.filter(f => f.uid !== uploadFile.uid)
      return
    }
    emit('file-selected', uploadFile.raw)
  }
}

function onRemove() {}

function handleExceed() {
  ElMessage.warning(`最多上传 ${props.limit} 个文件`)
}

function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>
