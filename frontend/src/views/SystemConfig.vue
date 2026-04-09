<template>
  <div class="page-container">
    <div class="page-header">
      <h2>系统配置</h2>
      <el-button type="primary" @click="saveAll" :loading="saving">保存全部</el-button>
    </div>

    <el-tabs v-model="activeGroup">
      <el-tab-pane v-for="(configs, group) in groupedConfigs" :key="group" :label="groupLabels[group] || group" :name="group">
        <div v-for="item in configs" :key="item.key" style="margin-bottom:16px;">
          <div style="display:flex;align-items:center;gap:12px;">
            <span style="min-width:220px;font-weight:500;color:#333;">{{ item.key }}</span>
            <el-input v-model="item.value" style="flex:1" />
            <span style="color:#999;font-size:12px;min-width:200px;">{{ item.description }}</span>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import client from '../api'

const activeGroup = ref('system')
const saving = ref(false)
const groupedConfigs = reactive<Record<string, any[]>>({})
const groupLabels: Record<string, string> = {
  system: '系统设置',
  security: '安全配置',
  notification: '通知设置',
  work_order: '工单设置',
  upload: '上传设置',
}

async function loadConfigs() {
  try {
    const { data } = await client.get('/system-config/')
    Object.assign(groupedConfigs, data)
    if (!activeGroup.value || !groupedConfigs[activeGroup.value]) {
      const keys = Object.keys(groupedConfigs)
      if (keys.length) activeGroup.value = keys[0]
    }
  } catch { ElMessage.error('加载配置失败') }
}

async function saveAll() {
  const allConfigs: any[] = []
  for (const [group, items] of Object.entries(groupedConfigs)) {
    for (const item of items) {
      allConfigs.push({ key: item.key, value: item.value, group })
    }
  }
  saving.value = true
  try {
    await client.put('/system-config/batch', allConfigs)
    ElMessage.success('保存成功')
  } catch { ElMessage.error('保存失败') }
  finally { saving.value = false }
}

onMounted(loadConfigs)
</script>
