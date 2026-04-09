<template>
  <div class="bg-white p-6 rounded-xl shadow-sm border border-f0f0f0">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-lg font-bold">吏部名册 (实时)</h2>
    </div>

    <el-table :data="users" border stripe>
      <el-table-column prop="username" label="名讳" width="120" />
      <el-table-column prop="display_name" label="姓名" width="120" />
      <el-table-column prop="department" label="所属部衙" />
      <el-table-column label="职级角色">
        <template #default="scope">
          <el-tag effect="light">{{ scope.row.role }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="入府日期" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getUsers } from '../api'

const users = ref([])

onMounted(async () => {
  users.value = await getUsers()
})
</script>
