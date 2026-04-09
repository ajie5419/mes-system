# 制造业生产管理系统 API 契约 (v1.4.0)

## 0. 认证 (Authentication)
所有业务接口需在请求头携带 `Authorization: Bearer {access_token}`，未认证返回 `401 Unauthorized`。

### POST /api/v1/auth/register
- **描述**：注册新用户，注册成功自动登录返回 token
- **请求体**：
  ```json
  { "username": "string", "display_name": "string", "password": "string", "department": "技术部|工艺部|采购部|生产部|项目管理部", "role": "Admin|Manager|Worker" }
  ```
- **响应** `201`：
  ```json
  { "access_token": "string", "refresh_token": "string", "token_type": "bearer", "user": { "id": 1, "username": "...", "display_name": "...", "department": "...", "role": "...", "is_active": true, "created_at": "..." } }
  ```

### POST /api/v1/auth/login
- **描述**：用户登录
- **请求体**：`{ "username": "string", "password": "string" }`
- **响应** `200`：同 register 响应
- **错误** `401`：用户名或密码错误

### POST /api/v1/auth/refresh
- **描述**：用 refresh_token 换取新 access_token
- **请求体**：`{ "refresh_token": "string" }`
- **响应** `200`：`{ "access_token": "string", "token_type": "bearer" }`

### GET /api/v1/auth/me
- **描述**：获取当前认证用户信息
- **响应** `200`：`{ "id": 1, "username": "...", ... }`

---

## 1. 组织架构管理 (Organization)
### POST /api/v1/users/
- **描述**：招纳新人。
- **参数**：`username`, `display_name`, `department`, `role`.

### GET /api/v1/users/
- **描述**：获取府内修行者名册。

## 2. 工单决策中心 (Work Order)
### POST /api/v1/work-orders/
- **描述**：创建新生产任务。
- **逻辑**：自动编号 (WO-YYYYMMDD-NNN)，初始化 17 个关键节点。

### GET /api/v1/work-orders/
- **描述**：工单列表，支持状态与关键词筛选。

## 3. 变更与锁定 (Change & Lock)
### POST /api/v1/changes/
- **描述**：发起变更，自动锁定相关工单。
- **状态流转**：工单状态变为 `Blocked`, `is_locked = true`。

### POST /api/v1/changes/{id}/confirm
- **描述**：部门签押。
- **逻辑**：所有关联部门确认后，工单自动恢复 `InProgress`。

## 4. 生产进度 (Progress)
### POST /api/v1/progress/report
- **校验**：若 `is_locked = true`，返回 423 拒绝汇报。
- **逻辑**：自动计算 `deviation_days` 并更新健康度（红黄绿）。

## 5. 质量与扩展模块 (Quality & Extra)
### GET /api/v1/extra/quality-issues
- **描述**：获取不合格品项清单。

### POST /api/v1/extra/quality-issues
- **描述**：记录新发现的缺陷。

### GET /api/v1/extra/suppliers
- **描述**：审阅供应商名录。

### GET /api/v1/extra/drawings
- **描述**：查阅版本图纸。

## 6. 指标看板 (Dashboard)
### GET /api/v1/dashboard/summary
- **描述**：获取汇总指标与漏报预警。

## 权限体系

### 权限列表

| 权限编码 | 描述 | 所属模块 |
|----------|------|----------|
| work_orders:read | 查看工单 | work_orders |
| work_orders:create | 创建工单 | work_orders |
| work_orders:update | 编辑工单 | work_orders |
| work_orders:delete | 删除工单 | work_orders |
| users:read | 查看用户 | users |
| users:create | 创建用户 | users |
| users:update | 编辑用户 | users |
| changes:read | 查看变更 | changes |
| changes:create | 发起变更 | changes |
| changes:confirm | 确认变更 | changes |
| progress:read | 查看进度 | progress |
| progress:report | 汇报进度 | progress |
| extra:read | 查看扩展模块 | extra |
| extra:create | 管理扩展模块 | extra |
| dashboard:read | 查看看板 | dashboard |
| audit:read | 查看审计日志 | audit |

### 角色-权限矩阵

| 权限 | Admin | Manager | Worker |
|------|:-----:|:-------:|:------:|
| work_orders:read | ✅ | ✅ | ✅ |
| work_orders:create | ✅ | ✅ | ❌ |
| work_orders:update | ✅ | ✅ | ❌ |
| work_orders:delete | ✅ | ❌ | ❌ |
| users:read | ✅ | ✅ | ❌ |
| users:create | ✅ | ✅ | ❌ |
| users:update | ✅ | ✅ | ❌ |
| changes:read | ✅ | ✅ | ❌ |
| changes:create | ✅ | ✅ | ❌ |
| changes:confirm | ✅ | ✅ | ❌ |
| progress:read | ✅ | ✅ | ✅ |
| progress:report | ✅ | ✅ | ✅ |
| extra:read | ✅ | ✅ | ✅ |
| extra:create | ✅ | ✅ | ❌ |
| dashboard:read | ✅ | ✅ | ✅ |
| audit:read | ✅ | ✅ | ❌ |

### 权限管理接口

#### GET /api/v1/permissions
获取所有权限（按模块分组）。需认证。

#### GET /api/v1/permissions/roles
获取角色-权限映射。需认证。

#### PUT /api/v1/permissions/roles/{role}
更新角色权限。仅 Admin 可操作。

**请求体：**
```json
{
  "permission_codes": ["work_orders:read", "work_orders:create"]
}
```

---

## 操作日志 (Audit)

### 查询操作日志
`GET /api/v1/audit/logs`

**权限**: `audit:read`（Admin、Manager）

| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | int | 按用户ID筛选 |
| action | string | 操作类型：create/read/update/delete/login/logout |
| resource_type | string | 资源类型：work_order/user/change/progress/supplier/drawing/quality_issue |
| start_date | string | 起始日期 (ISO) |
| end_date | string | 截止日期 (ISO) |
| page | int | 页码 (默认1) |
| page_size | int | 每页条数 (默认20, 最大100) |

**响应**:
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "username": "admin",
      "action": "create",
      "resource_type": "work_order",
      "resource_id": 42,
      "detail": "{\"project_name\":\"新项目\"}",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2026-04-09T10:00:00"
    }
  ]
}
```

### 查看日志详情
`GET /api/v1/audit/logs/{id}`

**权限**: `audit:read`


---

## 甘特图排程 (v1.6.0)

### GET /api/v1/work-orders/gantt-data
- **描述**：获取甘特图排程数据，含里程碑实际进度与计划对比
- **参数**：
  - `wo_id` (可选, int) — 指定工单ID，不传则返回所有进行中工单
- **权限**: `work_orders:read`
- **响应** `200`：
  ```json
  [
    {
      "id": 1,
      "wo_number": "WO-20260409-001",
      "project_name": "项目A",
      "status": "InProgress",
      "total_progress": 45.5,
      "planned_delivery_date": "2026-06-01",
      "milestones": [
        {
          "node_name": "技术出图",
          "planned_start_date": "2026-04-10",
          "planned_end_date": "2026-04-20",
          "actual_start_date": "2026-04-11",
          "actual_end_date": null,
          "completion_rate": 60.0,
          "status": "InProgress",
          "deviation_days": 3
        }
      ]
    }
  ]
  ```

---

## 文件上传 (v1.5.0)

### 上传文件
`POST /api/v1/upload`
- Content-Type: `multipart/form-data`
- 参数: `file` (必填), `directory` (可选子目录)
- 返回: `{id, file_name, file_path, file_size, file_type, uploaded_at}`
- **权限**: `upload`
- 文件类型白名单: pdf, dwg, dxf, jpg, png, doc, docx, xls, xlsx, zip, rar
- 单文件限制 50MB

### 下载/预览文件
`GET /api/v1/upload/{file_path:path}`
- **权限**: `upload`

### 删除文件
`DELETE /api/v1/upload`
- Body: `{"file_path": "..."}`
- **权限**: `upload`

### 图纸上传（含文件）
`POST /api/v1/extra/drawings`
- Content-Type: `multipart/form-data`
- 参数: `wo_id` (必填), `version`, `file` (可选)
- **权限**: `extra:create`


---

## 通知系统

### 获取当前用户通知列表
`GET /api/v1/notifications`
- 查询参数: `unread_only` (bool), `page` (int), `page_size` (int)
- **权限**: 认证用户

### 获取未读通知数量
`GET /api/v1/notifications/unread-count`
- **权限**: 认证用户

### 标记通知已读
`PUT /api/v1/notifications/{id}/read`
- **权限**: 通知所属用户

### 全部标记已读
`PUT /api/v1/notifications/read-all`
- **权限**: 认证用户

### 删除通知
`DELETE /api/v1/notifications/{id}`
- **权限**: 通知所属用户

## Webhook 管理

### 获取 Webhook 配置列表
`GET /api/v1/webhook/config`
- **权限**: Admin

### 创建 Webhook 配置
`POST /api/v1/webhook/config`
- Body: `{ name, url, type (wechat/dingtalk/custom), is_enabled }`
- **权限**: Admin

### 更新 Webhook 配置
`PUT /api/v1/webhook/config/{config_id}`
- **权限**: Admin

### 删除 Webhook 配置
`DELETE /api/v1/webhook/config/{config_id}`
- **权限**: Admin

### 测试 Webhook 发送
`POST /api/v1/webhook/test`
- Body: `{ config_id, title, content }`
- **权限**: Admin

## 数据导出

所有导出接口返回 Excel 文件（.xlsx），需要对应模块的 `read` 权限。

### GET /api/v1/export/work-orders
导出工单列表 Excel。

| 参数 | 类型 | 说明 |
|------|------|------|
| status | string | 筛选状态 |
| keyword | string | 搜索工单号/项目名 |
| is_delayed | boolean | 是否延期 |

### GET /api/v1/export/work-orders/{wo_id}
导出单个工单详情 Excel，包含三个 Sheet：基本信息、里程碑进度、进度汇报历史。

### GET /api/v1/export/progress
导出进度汇总 Excel（工单+里程碑关联）。

### GET /api/v1/export/audit-logs
导出操作日志 Excel。

| 参数 | 类型 | 说明 |
|------|------|------|
| user_id | int | 筛选用户 |
| action | string | 操作类型 |
| resource_type | string | 资源类型 |
| start_date | string | 起始日期 |
| end_date | string | 截止日期 |

### GET /api/v1/export/users
导出用户列表 Excel。
## 打印模板 API

### 获取工单打印数据
`GET /api/v1/print/work-order/{wo_id}`

**权限**: `work_orders:read`

返回工单完整打印数据，包含基本信息、里程碑、最近10条进度汇报、变更记录、质量问题。

**响应示例**:
```json
{
  "work_order": { "wo_number": "...", "project_name": "...", ... },
  "milestones": [...],
  "recent_reports": [...],
  "change_records": [...],
  "quality_issues": [...]
}
```

### 获取进度报告打印数据
`GET /api/v1/print/progress-report/{wo_id}`

**权限**: `progress:read`

返回工单进度报告打印数据，包含基本信息、里程碑汇总、全部进度汇报记录。

**响应示例**:
```json
{
  "work_order": { "wo_number": "...", ... },
  "milestones": [...],
  "reports": [...]
}
```


---

## WebSocket 实时通知

### 连接方式

```
ws://{host}/api/v1/ws/notifications?token={jwt_token}
```

- 使用 JWT token 进行认证（通过 query parameter 传递，因 WebSocket 握手不支持自定义 header）
- 连接成功后需发送心跳消息保持连接，服务端 60 秒无心跳自动断开

### 心跳机制

客户端每 30 秒发送文本 `"ping"`，服务端回复 `"pong"`。超过 60 秒未收到心跳则关闭连接。

### 推送消息格式

```json
{
  "type": "notification | system | alert",
  "data": {
    "id": 123,
    "title": "通知标题",
    "content": "通知内容",
    "resource_type": "work_order",
    "resource_id": 456
  },
  "timestamp": "2026-04-09T15:30:00+08:00"
}
```

### 连接状态

前端通过状态指示器显示 WebSocket 连接状态：
- 🟢 绿色 = 已连接
- 🟡 黄色闪烁 = 重连中
- 🔴 红色 = 已断开

### 断线重连

采用指数退避策略：3s → 6s → 12s → 30s → 30s，最多重试 5 次。重连失败后自动降级为 30 秒轮询保底。

## 9. 数据大屏 (BigScreen)

### GET /api/v1/bigscreen/overview

获取数据驾驶舱汇总数据。权限：`dashboard:read`

**响应示例：**
```json
{
  "total": 150,
  "in_progress": 42,
  "completed": 88,
  "overdue": 7,
  "today_new": 3,
  "today_done": 5,
  "completion_rate": 58.7,
  "overdue_rate": 4.7,
  "health_distribution": { "GREEN": 120, "YELLOW": 23, "RED": 7 },
  "department_distribution": { "技术部": 45, "生产部": 60, "工艺部": 25 },
  "trend": [
    { "date": "04-03", "new": 5, "completed": 3 },
    { "date": "04-04", "new": 2, "completed": 4 }
  ],
  "priority_distribution": { "1": 10, "2": 25, "3": 80, "4": 35 },
  "recent_logs": [
    { "id": 1, "username": "admin", "action": "create", "resource_type": "work_order", "detail": "创建工单", "created_at": "2026-04-09 10:00:00" }
  ]
}
```
