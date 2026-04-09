# MES API 规格文档

基础路径：`/api/v1`（部分系统管理模块使用 `/` 前缀）

认证方式：Bearer Token（JWT）

---

## 认证 `/api/v1/auth`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /login | 登录 | 无 |
| POST | /register | 注册 | 无 |
| POST | /refresh | 刷新 Token | 已登录 |
| GET | /me | 当前用户信息 | 已登录 |

## 工单管理 `/api/v1/work-orders`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 工单列表（分页、筛选） |
| POST | / | 创建工单 |
| GET | /{wo_id} | 工单详情 |
| PUT | /{wo_id} | 更新工单 |
| DELETE | /{wo_id} | 删除工单 |
| GET | /gantt-data | 甘特图数据 |
| GET | /{wo_id}/timeline | 工单时间线 |
| GET | /{wo_id}/assignees | 工单协作人 |
| POST | /{wo_id}/assignees | 分配部门 |

## 变更控制 `/api/v1/changes`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 变更列表 |
| POST | / | 创建变更 |
| POST | /{change_id}/confirm | 确认变更 |

## 进度汇报 `/api/v1/progress`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /report | 汇报进度 |
| GET | /{wo_id} | 查询进度 |

## 看板 `/api/v1/dashboard`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /summary | 看板汇总 |

## 用户管理 `/api/v1/users`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 用户列表 |
| POST | / | 创建用户 |
| PATCH | /{user_id} | 更新用户 |

## 权限管理 `/api/v1/permissions`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 权限列表 |
| GET | /roles | 角色权限 |
| PUT | /roles/{role} | 更新角色权限 |

## 扩展模块 `/api/v1/extra`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /quality-issues | 不合格品列表 |
| POST | /quality-issues | 创建不合格品 |
| GET | /suppliers | 供应商列表 |
| POST | /suppliers | 创建供应商 |
| PUT | /suppliers/{sid} | 更新供应商 |
| DELETE | /suppliers/{sid} | 删除供应商 |
| GET | /drawings | 图纸列表 |
| POST | /drawings | 创建图纸 |

## 操作日志 `/api/v1/audit`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /logs | 日志列表 |
| GET | /logs/{log_id} | 日志详情 |

## 文件上传 `/api/v1/upload`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | / | 上传文件 |
| DELETE | /{file_path} | 删除文件 |

## 通知 `/api/v1/notifications`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 通知列表 |
| GET | /unread-count | 未读数量 |
| PUT | /{notification_id}/read | 标记已读 |
| PUT | /read-all | 全部已读 |
| DELETE | /{notification_id} | 删除通知 |

## Webhook `/api/v1/webhook`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /config | 配置列表 |
| POST | /config | 创建配置 |
| PUT | /config/{id} | 更新配置 |
| DELETE | /config/{id} | 删除配置 |
| POST | /test | 测试推送 |

## 打印 `/api/v1/print`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /work-order/{wo_id} | 工单打印数据 |
| GET | /progress-report/{wo_id} | 进度报告打印数据 |

## 数据大屏 `/api/v1/bigscreen`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /overview | 大屏概况 |

## 部门管理 `/departments`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 部门树 |
| GET | /flat | 部门平铺列表 |
| POST | / | 创建部门 |
| PUT | /{dept_id} | 更新部门 |
| DELETE | /{dept_id} | 删除部门 |

## 系统配置 `/system-config`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /config | 配置列表 |
| POST | /config | 创建配置 |
| PUT | /config/{config_id} | 更新配置 |
| GET | /value/{key} | 按键查询 |
| PUT | /batch | 批量更新 |

## 工单模板 `/templates`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 模板列表 |
| GET | /{template_id} | 模板详情 |

## 任务看板 `/task-board`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /departments | 部门看板概览 |
| GET | /department/{dept_id} | 部门任务列表 |
| POST | /tasks | 创建任务 |
| PUT | /tasks/{task_id} | 更新任务 |
| DELETE | /tasks/{task_id} | 删除任务 |
| PUT | /tasks/{task_id}/move | 移动任务 |

## 审批流 `/approvals`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /flows | 审批流程列表 |
| POST | /flows | 创建流程 |
| POST | /start | 发起审批 |
| GET | /pending | 待审批列表 |
| GET | /history/{wo_id} | 审批历史 |
| POST | /steps/{step_id}/approve | 审批通过 |
| POST | /steps/{step_id}/reject | 审批驳回 |

## 异常管理 `/exceptions`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 异常列表 |
| GET | /{exc_id} | 异常详情 |
| POST | / | 上报异常 |
| PUT | /{exc_id} | 更新异常 |
| PUT | /{exc_id}/escalate | 升级异常 |
| PUT | /{exc_id}/resolve | 关闭异常 |
| GET | /stats | 异常统计 |

## 自动化规则 `/api/v1/automation`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /rules | 规则列表 |
| POST | /rules | 创建规则 |
| PUT | /rules/{rule_id} | 更新规则 |
| DELETE | /rules/{rule_id} | 删除规则 |
| PUT | /rules/{rule_id}/toggle | 启用/禁用 |
| GET | /execution-log | 执行日志 |

## 评论系统 `/api/v1/comments`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /{resource_type}/{resource_id} | 评论列表 |
| POST | / | 创建评论 |
| DELETE | /{comment_id} | 删除评论 |

## 数据分析 `/api/v1/analytics`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /kpi | KPI 概览 |
| GET | /work-orders/trend | 工单趋势 |
| GET | /work-orders/cycle-time | 周期分析 |
| GET | /work-orders/on-time-rate | 准时率 |
| GET | /work-orders/overdue | 超期统计 |
| GET | /department/workload | 部门工作量 |
| GET | /department/efficiency | 部门效率 |
| GET | /exceptions/trend | 异常趋势 |
| GET | /exceptions/resolution | 异常解决率 |
| GET | /exceptions/by-type | 异常分类 |
| GET | /exceptions/by-department | 异常部门分布 |
| GET | /progress/streak | 进度连续打卡 |
| GET | /milestone/completion | 里程碑完成率 |

## 数据导出 `/export`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /report | 导出报告（Excel） |

## WebSocket

| 路径 | 说明 |
|------|------|
| /api/v1/ws/notifications | 实时通知推送 |

## 系统

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 健康检查 |
| GET | /health | 健康检查 |
