<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>MES 智造系统</h1>
        <p class="subtitle">制造业生产管理系统</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" :rules="rules" ref="loginRef" @keyup.enter="handleLogin">
            <el-form-item prop="username">
              <el-input v-model="loginForm.username" prefix-icon="User" placeholder="用户名" size="large" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="loginForm.password" prefix-icon="Lock" placeholder="密码" type="password" show-password size="large" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleLogin">登 录</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form :model="regForm" :rules="regRules" ref="regRef" @keyup.enter="handleRegister">
            <el-form-item prop="username">
              <el-input v-model="regForm.username" prefix-icon="User" placeholder="用户名" size="large" />
            </el-form-item>
            <el-form-item prop="display_name">
              <el-input v-model="regForm.display_name" prefix-icon="Postcard" placeholder="姓名" size="large" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="regForm.password" prefix-icon="Lock" placeholder="密码" type="password" show-password size="large" />
            </el-form-item>
            <el-form-item prop="department">
              <el-select v-model="regForm.department" placeholder="选择部门" size="large" style="width: 100%">
                <el-option v-for="d in departments" :key="d" :label="d" :value="d" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleRegister">注 册</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const emit = defineEmits<{ (e: 'success'): void }>()
const auth = useAuthStore()
const activeTab = ref('login')
const loading = ref(false)
const loginRef = ref<FormInstance>()
const regRef = ref<FormInstance>()

const departments = ['技术部', '工艺部', '采购部', '生产部', '项目管理部']

const loginForm = reactive({ username: '', password: '' })
const regForm = reactive({ username: '', display_name: '', password: '', department: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const regRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  display_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码至少6位', trigger: 'blur' }],
  department: [{ required: true, message: '请选择部门', trigger: 'change' }],
}

async function handleLogin() {
  await loginRef.value?.validate()
  loading.value = true
  try {
    await auth.login(loginForm.username, loginForm.password)
    ElMessage.success('登录成功')
    emit('success')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  await regRef.value?.validate()
  loading.value = true
  try {
    await auth.register({ ...regForm, role: 'Worker' })
    ElMessage.success('注册成功')
    emit('success')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0c1a2e 0%, #1a2942 50%, #0c1a2e 100%);
}
.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.login-header { text-align: center; margin-bottom: 24px; }
.login-header h1 { font-size: 24px; color: #1a2942; margin: 0 0 4px; }
.login-header .subtitle { color: #8c939d; font-size: 14px; margin: 0; }
.login-btn { width: 100%; }
</style>
