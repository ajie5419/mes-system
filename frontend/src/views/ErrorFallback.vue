<template>
  <div style="padding:40px;text-align:center;color:#999;">
    <p style="font-size:16px;margin-bottom:12px;">组件加载失败</p>
    <el-button size="small" type="primary" @click="$emit('retry')">重新加载</el-button>
  </div>
</template>
