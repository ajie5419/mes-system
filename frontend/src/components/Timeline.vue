<template>
  <div class="timeline-view" v-loading="loading">
    <div v-for="(item, idx) in events" :key="idx" class="timeline-item">
      <div class="timeline-left">
        <div class="timeline-dot" :style="{ background: item.color }"></div>
        <div v-if="idx < events.length - 1" class="timeline-line"></div>
      </div>
      <div class="timeline-card">
        <div class="timeline-header">
          <el-tag :color="item.color" effect="dark" size="small" style="border:none;">{{ item.action }}</el-tag>
          <span class="timeline-user">{{ item.user }}</span>
          <span class="timeline-time">{{ formatTime(item.timestamp) }}</span>
        </div>
        <div class="timeline-detail">{{ item.detail }}</div>
      </div>
    </div>
    <el-empty v-if="!loading && events.length === 0" description="暂无时间线记录" :image-size="60" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { getWorkOrderTimeline } from '../api'

const props = defineProps<{ woId: number }>()
const events = ref<any[]>([])
const loading = ref(true)

onMounted(() => loadTimeline())
watch(() => props.woId, () => loadTimeline())

async function loadTimeline() {
  if (!props.woId) return
  loading.value = true
  try {
    events.value = await getWorkOrderTimeline(props.woId)
  } catch { events.value = [] }
  finally { loading.value = false }
}

function formatTime(t: string) {
  if (!t) return ''
  const d = new Date(t)
  return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.timeline-view { padding: 8px 0; }
.timeline-item { display: flex; gap: 16px; min-height: 60px; }
.timeline-left { display: flex; flex-direction: column; align-items: center; width: 20px; flex-shrink: 0; }
.timeline-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; margin-top: 6px; }
.timeline-line { width: 2px; flex: 1; background: #e8e8e8; margin: 4px 0; }
.timeline-card { flex: 1; padding-bottom: 16px; }
.timeline-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.timeline-user { font-size: 13px; font-weight: 500; color: #333; }
.timeline-time { font-size: 12px; color: #999; margin-left: auto; }
.timeline-detail { font-size: 13px; color: #555; line-height: 1.5; }
</style>
