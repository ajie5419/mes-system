// 状态中文映射

export const STATUS_MAP: Record<string, string> = {
  // 工单状态
  Backlog: '待处理',
  InProgress: '进行中',
  Blocked: '已阻塞',
  Completed: '已完成',
  Archived: '已归档',

  // 健康状态
  GREEN: '正常',
  YELLOW: '预警',
  RED: '异常',

  // 用户角色
  Admin: '管理员',
  Manager: '经理',
  Worker: '操作工',

  // 部门
  技术部: '技术部',
  工艺部: '工艺部',
  采购部: '采购部',
  生产部: '生产部',
  项目管理部: '项目管理部',

  // 变更类型
  技术变更: '技术变更',
  工艺变更: '工艺变更',
  计划变更: '计划变更',

  // 审批状态
  Pending: '待审批',
  Approved: '已通过',
  Rejected: '已驳回',

  // 优先级
  high: '高',
  medium: '中',
  low: '低',
  High: '高',
  Medium: '中',
  Low: '低',

  // 任务状态
  todo: '待办',
  in_progress: '进行中',
  done: '已完成',
  Todo: '待办',
  Done: '已完成',

  // 异常等级
  critical: '严重',
  major: '重大',
  minor: '一般',
  Critical: '严重',
  Major: '重大',
  Minor: '一般',

  // 通知状态
  unread: '未读',
  read: '已读',
}

export function statusText(status: any): string {
  if (!status) return '-'
  return STATUS_MAP[status] || STATUS_MAP[String(status)] || String(status)
}
