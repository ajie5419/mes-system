<template>
  <el-button :icon="Printer" :type="type" size="small" @click="handlePrint" :disabled="!resourceId">
    <slot>打印</slot>
  </el-button>
</template>

<script setup lang="ts">
import { Printer } from '@element-plus/icons-vue'
import { getWorkOrderPrintData, getProgressReportPrintData } from '../api'
import PrintPreview from '../views/PrintPreview.vue'
import { createApp, h } from 'vue'

const props = defineProps<{
  type: 'work-order' | 'progress-report'
  resourceId?: number
  buttonType?: string
}>()

function handlePrint() {
  const mountEl = document.createElement('div')
  mountEl.id = 'print-preview-overlay'
  mountEl.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;z-index:9999;background:#f5f5f5;'
  document.body.appendChild(mountEl)

  const app = createApp(PrintPreview, {
    printType: props.type,
    resourceId: props.resourceId!,
    onClose: () => {
      app.unmount()
      mountEl.remove()
    }
  })
  app.mount(mountEl)
}
</script>
