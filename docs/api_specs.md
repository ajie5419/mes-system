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

