<template>
  <div class="comment-panel">
    <!-- 评论输入 -->
    <div class="comment-input-area">
      <el-input
        v-model="newComment"
        type="textarea"
        :rows="3"
        placeholder="输入评论，使用 @用户名 提及他人..."
        @keydown.ctrl.enter="submitComment"
      />
      <div class="comment-actions">
        <el-checkbox v-model="isInternal" size="small">内部备注</el-checkbox>
        <el-button type="primary" size="small" @click="submitComment" :loading="submitting">
          发布 (Ctrl+Enter)
        </el-button>
      </div>
    </div>

    <!-- 评论列表 -->
    <div class="comment-list" v-loading="loading">
      <div v-for="c in comments" :key="c.id" class="comment-item">
        <div class="comment-main">
          <el-avatar :size="28" class="comment-avatar">{{ c.username?.[0] || '?' }}</el-avatar>
          <div class="comment-body">
            <div class="comment-header">
              <span class="comment-author">{{ c.username }}</span>
              <el-tag v-if="c.is_internal" size="small" type="warning" effect="plain" style="margin-left:6px;">内部</el-tag>
              <span class="comment-time">{{ formatTime(c.created_at) }}</span>
              <el-button v-if="c.user_id === currentUserId" type="danger" text size="small" style="margin-left:auto;" @click="handleDelete(c.id)">删除</el-button>
            </div>
            <div class="comment-content">{{ c.content }}</div>
            <div class="comment-footer">
              <el-button text size="small" @click="startReply(c)">回复</el-button>
            </div>
          </div>
        </div>
        <!-- 回复列表 -->
        <div v-if="c.replies?.length" class="comment-replies">
          <div v-for="r in c.replies" :key="r.id" class="comment-item reply">
            <el-avatar :size="24" class="comment-avatar">{{ r.username?.[0] || '?' }}</el-avatar>
            <div class="comment-body">
              <div class="comment-header">
                <span class="comment-author">{{ r.username }}</span>
                <span class="comment-time">{{ formatTime(r.created_at) }}</span>
              </div>
              <div class="comment-content">{{ r.content }}</div>
            </div>
          </div>
        </div>
        <!-- 回复输入 -->
        <div v-if="replyingTo === c.id" class="reply-input-area">
          <el-input v-model="replyContent" size="small" placeholder="输入回复..." @keydown.enter="submitReply(c.id)" />
          <el-button type="primary" size="small" @click="submitReply(c.id)">发送</el-button>
          <el-button size="small" @click="replyingTo = null">取消</el-button>
        </div>
      </div>
      <el-empty v-if="!loading && comments.length === 0" description="暂无评论" :image-size="60" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getComments, createComment, deleteComment } from '../api'
import { useAuthStore } from '../stores/auth'

const props = defineProps<{ resourceType: string; resourceId: number; woId?: number }>()
const auth = useAuthStore()
const currentUserId = computed(() => auth.user?.id)

import { computed } from 'vue'

const comments = ref<any[]>([])
const newComment = ref('')
const isInternal = ref(false)
const submitting = ref(false)
const loading = ref(true)
const replyingTo = ref<number | null>(null)
const replyContent = ref('')

onMounted(() => loadComments())

async function loadComments() {
  loading.value = true
  try {
    comments.value = await getComments(props.resourceType, props.resourceId)
  } catch { comments.value = [] }
  finally { loading.value = false }
}

async function submitComment() {
  if (!newComment.value.trim()) return
  submitting.value = true
  try {
    await createComment({
      wo_id: props.woId || null,
      resource_type: props.resourceType,
      resource_id: props.resourceId,
      content: newComment.value.trim(),
      is_internal: isInternal.value,
    })
    newComment.value = ''
    isInternal.value = false
    await loadComments()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '发布失败')
  } finally { submitting.value = false }
}

function startReply(c: any) {
  replyingTo.value = c.id
  replyContent.value = `@${c.username} `
}

async function submitReply(parentId: number) {
  if (!replyContent.value.trim()) return
  try {
    await createComment({
      wo_id: props.woId || null,
      resource_type: props.resourceType,
      resource_id: props.resourceId,
      parent_id: parentId,
      content: replyContent.value.trim(),
    })
    replyContent.value = ''
    replyingTo.value = null
    await loadComments()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '回复失败')
  }
}

async function handleDelete(id: number) {
  try {
    await deleteComment(id)
    await loadComments()
  } catch { ElMessage.error('删除失败') }
}

function formatTime(t: string) {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.comment-panel { }
.comment-input-area { margin-bottom: 16px; }
.comment-actions { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.comment-list { max-height: 500px; overflow-y: auto; }
.comment-item { padding: 12px 0; border-bottom: 1px solid #f0f0f0; }
.comment-item:last-child { border-bottom: none; }
.comment-main { display: flex; gap: 10px; }
.comment-avatar { flex-shrink: 0; }
.comment-body { flex: 1; min-width: 0; }
.comment-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.comment-author { font-weight: 500; font-size: 13px; color: #333; }
.comment-time { font-size: 12px; color: #999; }
.comment-content { font-size: 13px; color: #555; line-height: 1.6; word-break: break-word; }
.comment-footer { margin-top: 4px; }
.comment-replies { margin-left: 38px; padding-left: 12px; border-left: 2px solid #e8e8e8; }
.reply { padding: 8px 0; display: flex; gap: 8px; }
.reply-input-area { display: flex; gap: 8px; align-items: center; margin-top: 8px; margin-left: 38px; }
.reply-input-area .el-input { flex: 1; }
</style>
