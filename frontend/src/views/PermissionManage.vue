<template>
  <div class="page-container">
    <div class="page-header">
      <h2>权限管理</h2>
    </div>

    <div class="perm-layout">
      <!-- Role selector -->
      <div class="role-panel">
        <h3>角色</h3>
        <div
          v-for="r in roles"
          :key="r"
          :class="['role-item', activeRole === r ? 'active' : '']"
          @click="activeRole = r"
        >
          {{ roleLabels[r] }}
        </div>
      </div>

      <!-- Permission matrix -->
      <div class="matrix-panel">
        <el-table :data="tableData" border stripe style="width: 100%">
          <el-table-column prop="name" label="权限" min-width="180" />
          <el-table-column prop="code" label="编码" min-width="180" />
          <el-table-column label="授权" width="80" align="center">
            <template #default="{ row }">
              <el-checkbox
                :model-value="isChecked(row.code)"
                :disabled="permStore.userRole !== 'Admin'"
                @change="(val: boolean) => toggle(row.code, val)"
              />
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top: 16px; text-align: right">
          <el-button type="primary" :disabled="permStore.userRole !== 'Admin'" @click="save" :loading="saving">
            保存修改
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePermissionStore } from '../stores/permission'
import { ElMessage } from 'element-plus'

const permStore = usePermissionStore()
const roles = ['Admin', 'Manager', 'Worker']
const roleLabels: Record<string, string> = { Admin: '管理员', Manager: '经理', Worker: '工人' }
const activeRole = ref('Admin')
const saving = ref(false)
const pendingChanges = ref<Set<string>>(new Set())

const tableData = computed(() => {
  const rows: { code: string; name: string; module: string }[] = []
  for (const [mod, perms] of Object.entries(permStore.permissions)) {
    for (const p of perms) {
      rows.push({ code: p.code, name: p.name, module: mod })
    }
  }
  return rows
})

function isChecked(code: string): boolean {
  const base = (permStore.rolePermissions[activeRole.value] || []).includes(code)
  return pendingChanges.value.has(code) ? !base : base
}

function toggle(code: string, val: boolean) {
  const base = (permStore.rolePermissions[activeRole.value] || []).includes(code)
  if (val === base) {
    pendingChanges.value.delete(code)
  } else {
    pendingChanges.value.add(code)
  }
}

async function save() {
  if (pendingChanges.value.size === 0) {
    ElMessage.info('无变更')
    return
  }
  saving.value = true
  const base = new Set(permStore.rolePermissions[activeRole.value] || [])
  for (const code of pendingChanges.value) {
    if (base.has(code)) base.delete(code)
    else base.add(code)
  }
  try {
    await permStore.updateRolePermissions(activeRole.value, Array.from(base))
    pendingChanges.value.clear()
    ElMessage.success('保存成功')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await Promise.all([permStore.fetchPermissions(), permStore.fetchRolePermissions()])
})
</script>

<style scoped>
.perm-layout { display: flex; gap: 24px; }
.role-panel { width: 160px; flex-shrink: 0; }
.role-panel h3 { margin-bottom: 12px; font-size: 14px; color: #666; }
.role-item {
  padding: 10px 16px; border-radius: 6px; cursor: pointer;
  margin-bottom: 4px; font-size: 14px; color: #555; transition: all .2s;
}
.role-item:hover { background: #f5f5f5; }
.role-item.active { background: #e6f7ff; color: #1890ff; font-weight: 500; }
.matrix-panel { flex: 1; }
</style>
