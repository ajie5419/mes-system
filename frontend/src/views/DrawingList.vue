<template>
  <div class="bg-white p-6 rounded-xl shadow-sm border border-f0f0f0">
    <h2 class="text-lg font-bold mb-6">图纸百宝库</h2>
    <el-table :data="drawings" border>
      <el-table-column prop="version" label="版本号" width="120" />
      <el-table-column prop="wo_id" label="所属工单" width="120" />
      <el-table-column prop="file_url" label="存取路径" />
      <el-table-column prop="created_at" label="入库时间" />
    </el-table>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getDrawings } from '../api'
const drawings = ref([])
onMounted(async () => { drawings.value = await getDrawings() })
</script>
