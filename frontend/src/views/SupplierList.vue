<template>
  <div class="bg-white p-6 rounded-xl shadow-sm border border-f0f0f0">
    <h2 class="text-lg font-bold mb-6">供应商名录</h2>
    <el-table :data="suppliers" stripe>
      <el-table-column prop="name" label="商号" />
      <el-table-column prop="contact" label="联络方式" />
      <el-table-column label="信用评级">
        <template #default="scope"><el-tag>{{ scope.row.rating }}</el-tag></template>
      </el-table-column>
    </el-table>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getSuppliers } from '../api'
const suppliers = ref([])
onMounted(async () => { suppliers.value = await getSuppliers() })
</script>
