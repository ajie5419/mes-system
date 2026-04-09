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
      <!-- 状态流转按钮 -->
      <div class="status-flow" v-if="wo && !wo.is_locked">
        <el-button v-for="btn in availableTransitions" :key="btn.to" :type="btn.type" size="small" @click="transitionStatus(btn.to)">
          {{ btn.label }}
        </el-button>
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
          <div
            v-for="(m, i) in sortedMilestones"
            :key="m.id"
            class="milestone-row"
            draggable="true"
            @dragstart="onDragStart(i, $event)"
            @dragover.prevent="onDragOver(i)"
            @dragend="onDragEnd"
            :class="{ 'drag-over': dragOverIndex === i }"
          >
            <div class="milestone-left">
              <el-icon class="drag-handle" style="color:#ccc;font-size:14px;cursor:grab;"><Rank /></el-icon>
              <div :class="['milestone-dot', m.status === 'Completed' ? 'done' : m.status === 'InProgress' ? 'active' : 'pending']"></div>
              <div v-if="i < sortedMilestones.length - 1" :class="['milestone-line', m.status === 'Completed' ? 'done' : '']"></div>
            </div>
            <div class="milestone-content">
              <div class="milestone-header">
                <span class="milestone-name">{{ m.node_name }}</span>
                <el-tag :type="msTagType(m.status)" size="small">{{ m.status }}</el-tag>
                <el-button size="small" text type="primary" @click="openMilestoneEdit(m)">编辑</el-button>
              </div>
              <div v-if="m.planned_date" style="font-size:12px;color:#999;margin-top:2px;">计划日期：{{ m.planned_date }}</div>
              <div v-if="m.remarks" style="font-size:12px;color:#666;margin-top:2px;">{{ m.remarks }}</div>
              <el-progress v-if="m.completion_rate != null" :percentage="m.completion_rate" :stroke-width="6"
                :color="m.completion_rate >= 100 ? '#52c41a' : '#1890ff'" style="width:200px; margin-top:4px;" />
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无里程碑数据" />
      </el-card>

      <!-- 内联进度汇报 -->
      <el-card shadow="never" class="mb-4" v-if="wo.status !== 'Completed' && wo.status !== 'Archived'">
        <template #header><span class="section-title">进度汇报</span></template>
        <div class="inline-report">
          <div class="report-row">
            <label>汇报节点</label>
            <el-select v-model="inlineReport.milestone_id" placeholder="选择节点" style="width:200px" size="default">
              <el-option v-for="m in wo.milestones" :key="m.id" :label="m.node_name" :value="m.id" />
            </el-select>
          </div>
          <div class="report-row">
            <label>完成比例</label>
            <el-slider v-model="inlineReport.completion_rate" :min="0" :max="100" show-input style="flex:1;max-width:400px;" />
          </div>
          <div class="report-row">
            <label>备注</label>
            <el-input v-model="inlineReport.remarks" type="textarea" :rows="2" placeholder="可选备注" style="flex:1;max-width:400px;" />
          </div>
          <el-button type="primary" size="small" @click="handleInlineReport" :loading="reportSubmitting">
            提交汇报
          </el-button>
        </div>
      </el-card>

      <!-- 关联信息面板 -->
      <el-card shadow="never" class="mb-4">
        <template #header><span class="section-title">关联信息</span></template>
        <el-tabs>
          <el-tab-pane label="变更记录" v-if="relatedChanges.length">
            <el-table :data="relatedChanges" size="small" stripe>
              <el-table-column prop="change_type" label="类型" width="100" />
              <el-table-column prop="description" label="描述" show-overflow-tooltip />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'Approved' ? 'success' : row.status === 'Rejected' ? 'danger' : 'warning'" size="small">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="时间" width="170">
                <template #default="{ row }">{{ fmtDt(row.created_at) }}</template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="质量问题" v-if="relatedQuality.length">
            <el-table :data="relatedQuality" size="small" stripe>
              <el-table-column prop="title" label="标题" show-overflow-tooltip />
              <el-table-column prop="severity" label="严重度" width="100" />
              <el-table-column prop="status" label="状态" width="100" />
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="操作日志" v-if="auditLogs.length">
            <el-table :data="auditLogs" size="small" stripe>
              <el-table-column prop="action" label="操作" width="120" />
              <el-table-column prop="details" label="详情" show-overflow-tooltip />
              <el-table-column prop="created_at" label="时间" width="170">
                <template #default="{ row }">{{ fmtDt(row.created_at) }}</template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
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

    <!-- 里程碑编辑弹窗 -->
    <el-dialog v-model="showMilestoneEdit" title="编辑里程碑" width="420px" destroy-on-close>
      <el-form label-width="90px">
        <el-form-item label="计划日期">
          <el-date-picker v-model="editingMilestone.planned_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editingMilestone.remarks" type="textarea" :rows="3" placeholder="输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMilestoneEdit = false">取消</el-button>
        <el-button type="primary" @click="saveMilestoneEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { ArrowLeft, Rank } from '@element-plus/icons-vue'
import ExportButton from '../components/ExportButton.vue'
import PrintButton from '../components/PrintButton.vue'
import { ElMessage } from 'element-plus'
import { getWorkOrder, getProgress, getDrawings, createDrawingWithFile, updateWorkOrder, reportProgress, getChanges, getQualityIssues, getAuditLogs } from '../api'
import FileUpload from '../components/FileUpload.vue'

const props = defineProps<{ woId?: number }>()
const emit = defineEmits<{ (e: 'navigate', p: { id: string; name: string }): void }>()

const loading = ref(true)
const wo = ref<any>(null)
const progressHistory = ref<any[]>([])
const relatedDrawings = ref<any[]>([])
const relatedChanges = ref<any[]>([])
const relatedQuality = ref<any[]>([])
const auditLogs = ref<any[]>([])
const reportSubmitting = ref(false)

// ── 状态流转 ──
const statusFlow: Record<string, string[]> = {
  Backlog: ['InProgress'],
  InProgress: ['Completed', 'Blocked'],
  Blocked: ['InProgress'],
  Completed: ['Archived'],
}

const flowLabels: Record<string, { to: string; label: string; type: string }[]> = {
  Backlog: [{ to: 'InProgress', label: '开始执行', type: 'primary' }],
  InProgress: [
    { to: 'Completed', label: '标记完成', type: 'success' },
    { to: 'Blocked', label: '标记阻塞', type: 'danger' },
  ],
  Blocked: [{ to: 'InProgress', label: '恢复执行', type: 'primary' }],
  Completed: [{ to: 'Archived', label: '归档', type: 'info' }],
}

const availableTransitions = computed(() => {
  if (!wo.value) return []
  return flowLabels[wo.value.status] || []
})

async function transitionStatus(to: string) {
  if (!wo.value) return
  try {
    await updateWorkOrder(wo.value.id, { status: to })
    ElMessage.success(`状态已变更为 ${to}`)
    await loadDetail(wo.value.id)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '状态变更失败')
  }
}

// ── 里程碑拖拽排序 ──
const dragOverIndex = ref<number | null>(null)
let dragFromIndex = 0

function onDragStart(index: number, e: DragEvent) {
  dragFromIndex = index
  e.dataTransfer!.effectAllowed = 'move'
}

function onDragOver(index: number) {
  dragOverIndex.value = index
}

async function onDragEnd() {
  dragOverIndex.value = null
  if (!wo.value?.milestones) return
  const arr = [...wo.value.milestones]
  const [moved] = arr.splice(dragFromIndex, 1)
  arr.splice(dragOverIndex ?? dragFromIndex, 0, moved)
  wo.value.milestones = arr
  // Update sort_order via API
  try {
    await updateWorkOrder(wo.value.id, {
      milestone_order: arr.map((m: any) => m.id),
    } as any)
    ElMessage.success('里程碑顺序已更新')
  } catch {
    ElMessage.error('排序保存失败')
    await loadDetail(wo.value.id)
  }
}

const sortedMilestones = computed(() => wo.value?.milestones || [])

// ── 里程碑编辑 ──
const showMilestoneEdit = ref(false)
const editingMilestone = reactive({ id: 0, planned_date: '', remarks: '', _index: -1 })

function openMilestoneEdit(m: any) {
  editingMilestone.id = m.id
  editingMilestone.planned_date = m.planned_date || ''
  editingMilestone.remarks = m.remarks || ''
  editingMilestone._index = (wo.value?.milestones || []).findIndex((x: any) => x.id === m.id)
  showMilestoneEdit.value = true
}

async function saveMilestoneEdit() {
  if (!wo.value || editingMilestone._index < 0) return
  const milestones = [...wo.value.milestones]
  milestones[editingMilestone._index] = {
    ...milestones[editingMilestone._index],
    planned_date: editingMilestone.planned_date,
    remarks: editingMilestone.remarks,
  }
  wo.value.milestones = milestones
  showMilestoneEdit.value = false
  ElMessage.success('里程碑已更新')
}

// ── 内联进度汇报 ──
const inlineReport = reactive({ milestone_id: '' as any, completion_rate: 0, remarks: '' })

async function handleInlineReport() {
  if (!wo.value || !inlineReport.milestone_id) {
    ElMessage.warning('请选择汇报节点')
    return
  }
  reportSubmitting.value = true
  try {
    await reportProgress({
      wo_id: wo.value.id,
      milestone_id: inlineReport.milestone_id,
      completion_rate: inlineReport.completion_rate,
      remarks: inlineReport.remarks,
      report_date: new Date().toISOString().slice(0, 10),
    })
    ElMessage.success('进度已入库')
    inlineReport.milestone_id = ''
    inlineReport.completion_rate = 0
    inlineReport.remarks = ''
    progressHistory.value = await getProgress(wo.value.id)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '汇报失败')
  } finally {
    reportSubmitting.value = false
  }
}

// ── 加载数据 ──
const loadDetail = async (id: number) => {
  loading.value = true
  try {
    wo.value = await getWorkOrder(id)
    progressHistory.value = await getProgress(id)
    await loadDrawings()
    await loadRelatedInfo()
  } catch (e: any) {
    ElMessage.error('加载工单详情失败')
  }
  finally { loading.value = false }
}

watch(() => props.woId, (id) => {
  if (id) loadDetail(id)
}, { immediate: true })

defineExpose({ loadDetail })

async function loadDrawings() {
  if (!wo.value) return
  const all = await getDrawings() || []
  relatedDrawings.value = all.filter((d: any) => d.wo_id === wo.value.id)
}

async function loadRelatedInfo() {
  if (!wo.value) return
  try {
    const changes = await getChanges()
    relatedChanges.value = changes.filter((c: any) => c.wo_id === wo.value.id)
  } catch { relatedChanges.value = [] }
  try {
    const issues = await getQualityIssues()
    relatedQuality.value = issues.filter((q: any) => q.wo_id === wo.value.id)
  } catch { relatedQuality.value = [] }
  try {
    const logs = await getAuditLogs({ page_size: 50 })
    auditLogs.value = (logs.items || logs).filter((l: any) => l.wo_id === wo.value.id || l.resource_id === wo.value.id)
  } catch { auditLogs.value = [] }
}

function onQuickUpload(file: File) { /* placeholder */ }

const fmtDate = (d: string) => d ? d.slice(0, 10) : '—'
const fmtDateTime = (d: string) => d ? d.replace('T', ' ').slice(0, 19) : '—'
const fmtDt = (s: string) => s ? s.replace('T', ' ').slice(0, 19) : ''
const statusTagType = (s: string) => ({ Backlog: 'info', InProgress: 'primary', Blocked: 'danger', Completed: 'success', Archived: 'info' }[s] || 'info')
const healthTagType = (h: string) => ({ GREEN: 'success', YELLOW: 'warning', RED: 'danger' }[h] || 'info')
const healthLabel = (h: string) => ({ GREEN: '正常', YELLOW: '预警', RED: '延期' }[h] || h)
const progressColor = (p: number) => p >= 80 ? '#52c41a' : p >= 50 ? '#1890ff' : p >= 30 ? '#faad14' : '#ff4d4f'
const msTagType = (s: string) => ({ Completed: 'success', InProgress: 'primary', Pending: 'info', Blocked: 'danger' }[s] || 'info')
</script>

<style scoped>
.mb-4 { margin-bottom: 16px; }
.section-title { font-size: 15px; font-weight: 600; color: #333; }
.status-flow { display: flex; gap: 8px; }

.timeline-container { padding: 8px 0; }
.milestone-row { display: flex; gap: 12px; position: relative; padding: 4px 0; border-radius: 6px; transition: background .2s; }
.milestone-row.drag-over { background: #e6f7ff; }
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

.inline-report { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 16px; }
.inline-report .report-row { display: flex; align-items: center; gap: 8px; }
.inline-report .report-row label { font-size: 13px; color: #666; white-space: nowrap; }

.flex { display: flex; }
.items-center { align-items: center; }
.gap-3 { gap: 12px; }
</style>
