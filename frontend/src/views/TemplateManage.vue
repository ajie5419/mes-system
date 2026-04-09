<template>
  <div class="page-container">
    <div class="page-header">
      <h2>工单模板管理</h2>
    </div>

    <el-table :data="templates" border>
      <el-table-column prop="name" label="模板名称" min-width="200" />
      <el-table-column prop="industry_type" label="行业类型" width="140" />
      <el-table-column prop="node_count" label="节点数" width="80" align="center" />
      <el-table-column label="默认" width="80" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="success" size="small">是</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="viewDetail(row)">查看节点</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="detailVisible" :title="detailTemplate?.name || '模板详情'" width="600px">
      <el-table :data="milestones" border size="small">
        <el-table-column prop="sort_order" label="序号" width="60" />
        <el-table-column prop="node_name" label="节点名称" min-width="140" />
        <el-table-column prop="node_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="nodeTypeTag(row.node_type)" size="small">{{ row.node_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_required" label="必填" width="70" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.is_required" color="#67c23a"><Select /></el-icon>
            <el-icon v-else color="#ccc"><CloseBold /></el-icon>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Select, CloseBold } from '@element-plus/icons-vue'
import client from '../api'

const templates = ref<any[]>([])
const milestones = ref<any[]>([])
const detailVisible = ref(false)
const detailTemplate = ref<any>(null)

function nodeTypeTag(type: string) {
  return ({ '审批': 'warning', '执行': '', '检验': 'success', '交付': 'info' } as any)[type] || ''
}

async function loadTemplates() {
  try {
    const { data } = await client.get('/templates/')
    templates.value = data || []
  } catch {}
}

async function viewDetail(row: any) {
  detailTemplate.value = row
  try {
    const { data } = await client.get(`/templates/${row.id}`)
    milestones.value = data.milestones || []
  } catch { milestones.value = [] }
  detailVisible.value = true
}

onMounted(loadTemplates)
</script>
