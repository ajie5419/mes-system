<template>
  <div class="page-container" v-loading="loading">
    <div class="page-header">
      <div class="flex items-center gap-3">
        <PrintButton type="work-order" :resource-id="woId" button-type="primary">打印工单</PrintButton>
        <ExportButton export-type="work-order-detail" :params="{ id: woId }" label="导出详情" />
        <el-button :icon="ArrowLeft" text @click="$emit('navigate', { id: 'work-orders', name: '工单府库' })">返回</el-button>
        <h2>工单详情</h2>
        <el-tag v-if="wo" :type="statusTagType(wo.status)" size="small">{{ wo.status }}</el-tag>
        <el-tag v-if="wo?.is_locked" type="danger" size="small" effect="dark">已锁定</el-tag>
      </div>
    </div>

    <template v-if="wo">
      <!-- 基本信息 -->
      <el-card shadow="never" class="mb-4">
        <template #header><span class="section-title">基本信息</span></template>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="工单号">{{ wo.wo_number }}</el-descriptions-item>
          <el-descriptions-item label="项目名称">{{ wo.project_name }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ wo.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="计划交期">{{ fmtDate(wo.planned_delivery_date) }}</el-descriptions-item>
          <el-descriptions-item label="健康度">
            <el-tag :type="healthTagType(wo.health_status)" size="small" round>{{ healthLabel(wo.health_status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总进度">
            <el-progress :percentage="wo.overall_progress || 0" :stroke-width="10" :color="progressColor(wo.overall_progress)" style="width:120px" />
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ fmtDateTime(wo.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ fmtDateTime(wo.updated_at) }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 里程碑时间线 -->
      <el-card shadow="never" class="mb-4">
        <template #header><span class="section-title">里程碑进度</span></template>
        <div class="timeline-container" v-if="wo.milestones?.length">
          <div v-for="(m, i) in wo.milestones" :key="m.id" class="milestone-row">
            <div class="milestone-left">
              <div :class="['milestone-dot', m.status === 'Completed' ? 'done' : m.status === 'InProgress' ? 'active' : 'pending']"></div>
              <div v-if="i < wo.milestones.length - 1" :class="['milestone-line', m.status === 'Completed' ? 'done' : '']"></div>
            </div>
            <div class="milestone-content">
              <div class="milestone-header">
                <span class="milestone-name">{{ m.node_name }}</span>
                <el-tag :type="msTagType(m.status)" size="small">{{ m.status }}</el-tag>
              </div>
              <el-progress v-if="m.completion_rate != null" :percentage="m.completion_rate" :stroke-width="6"
                :color="m.completion_rate >= 100 ? '#52c41a' : '#1890ff'" style="width:200px; margin-top:4px;" />
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无里程碑数据" />
      </el-card>

      <!-- 关联图纸 -->
      <el-card shadow="never" class="mb-4">
        <template #header><span class="section-title">关联图纸</span></template>
        <el-table :data="relatedDrawings" stripe size="small" v-if="relatedDrawings.length">
          <el-table-column prop="version" label="版本" width="80" />
          <el-table-column label="文件" min-width="200">
            <template #default="{ row }">
              <el-link v-if="row.file_url" type="primary" :href="row.file_url" target="blank">{{ row.file_url.split('/').pop() }}</el-link>
              <span v-else class="text-gray-400">无文件</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="上传时间" width="170">
            <template #default="{ row }">{{ fmtDt(row.created_at) }}</template>
          </el-table-column>
        </el-table>
        <div class="mt-2">
          <FileUpload :limit="1" @file-selected="onQuickUpload" />
        </div>
      </el-card>

      <!-- 进度汇报历史 -->
      <el-card shadow="never">
        <template #header><span class="section-title">进度汇报记录</span></template>
        <el-table :data="progressHistory" stripe size="small" v-if="progressHistory.length">
          <el-table-column prop="milestone_id" label="节点ID" width="80" />
          <el-table-column prop="completion_rate" label="完成率" width="100">
            <template #default="{ row }">
              <el-progress :percentage="row.completion_rate" :stroke-width="6" style="width:80px" />
            </template>
          </el-table-column>
          <el-table-column prop="report_date" label="汇报日期" width="120">
            <template #default="{ row }">{{ fmtDate(row.report_date) }}</template>
          </el-table-column>
          <el-table-column prop="reporter" label="汇报人" width="100" />
          <el-table-column prop="remarks" label="备注" show-overflow-tooltip />
        </el-table>
        <el-empty v-else description="暂无汇报记录" />
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ArrowLeft } from '@element-plus/icons-vue'
import ExportButton from '../components/ExportButton.vue'
import PrintButton from '../components/PrintButton.vue'
import { watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getWorkOrder, getProgress, getDrawings, createDrawingWithFile } from '../api'
import FileUpload from '../components/FileUpload.vue'

const props = defineProps<{ woId?: number }>()
const emit = defineEmits<{ (e: 'navigate', p: { id: string; name: string }): void }>()

const loading = ref(true)
const wo = ref<any>(null)
const progressHistory = ref<any[]>([])

// 从 activeTab name 中提取 woId（如 "工单 WO-20260409-001"）
const woId = computed(() => {
  // 通过 event 传递更可靠，此处用 props
  return null
})

// 改用函数式加载
const loadDetail = async (id: number) => {
  loading.value = true
  try {
    wo.value = await getWorkOrder(id)
    progressHistory.value = await getProgress(id)
    await loadDrawings()
  } catch (e: any) {
    ElMessage.error('加载工单详情失败')
  }
  finally { loading.value = false }
}

// 暴露给父组件调用
watch(() => props.woId, (id) => {
  if (id) loadDetail(id)
}, { immediate: true })

defineExpose({ loadDetail })

const fmtDate = (d: string) => d ? d.slice(0, 10) : '—'
const fmtDateTime = (d: string) => d ? d.replace('T', ' ').slice(0, 19) : '—'
const statusTagType = (s: string) => ({ Backlog: 'info', InProgress: 'primary', Blocked: 'danger', Completed: 'success', Archived: 'info' }[s] || 'info')
const healthTagType = (h: string) => ({ GREEN: 'success', YELLOW: 'warning', RED: 'danger' }[h] || 'info')
const healthLabel = (h: string) => ({ GREEN: '正常', YELLOW: '预警', RED: '延期' }[h] || h)
const relatedDrawings = ref<any[]>([])
const quickFile = ref<File | null>(null)

async function loadDrawings() {
  if (!wo.value) return
  const all = await getDrawings() || []
  relatedDrawings.value = all.filter((d: any) => d.wo_id === wo.value.id)
}

function onQuickUpload(file: File) { quickFile.value = file }

async function quickUploadDrawing() {
  if (!quickFile.value || !wo.value) return
  try {
    await createDrawingWithFile({ wo_id: wo.value.id, version: 'V1.0', file: quickFile.value })
    ElMessage.success('图纸上传成功')
    quickFile.value = null
    await loadDrawings()
  } catch (e: any) {
    ElMessage.error('上传失败')
  }
}

function fmtDt(s: string) { return s ? s.replace('T',' ').slice(0,19) : '' }

const progressColor = (p: number) => p >= 80 ? '#52c41a' : p >= 50 ? '#1890ff' : p >= 30 ? '#faad14' : '#ff4d4f'
const msTagType = (s: string) => ({ Completed: 'success', InProgress: 'primary', Pending: 'info', Blocked: 'danger' }[s] || 'info')
</script>

<style scoped>
.mb-4 { margin-bottom: 16px; }
.section-title { font-size: 15px; font-weight: 600; color: #333; }

.timeline-container { padding: 8px 0; }
.milestone-row { display: flex; gap: 16px; position: relative; }
.milestone-left { display: flex; flex-direction: column; align-items: center; width: 20px; flex-shrink: 0; }
.milestone-dot {
  width: 14px; height: 14px; border-radius: 50%; border: 2px solid #d9d9d9; background: #fff;
  flex-shrink: 0; z-index: 1;
}
.milestone-dot.done { background: #52c41a; border-color: #52c41a; }
.milestone-dot.active { background: #1890ff; border-color: #1890ff; box-shadow: 0 0 0 4px rgba(24,144,255,.2); }
.milestone-dot.pending { border-color: #d9d9d9; }
.milestone-line { width: 2px; flex: 1; background: #e8e8e8; margin: 4px 0; min-height: 30px; }
.milestone-line.done { background: #52c41a; }
.milestone-content { flex: 1; padding-bottom: 24px; }
.milestone-header { display: flex; align-items: center; gap: 10px; }
.milestone-name { font-size: 14px; font-weight: 500; color: #333; }

.flex { display: flex; }
.items-center { align-items: center; }
.gap-3 { gap: 12px; }
</style>
