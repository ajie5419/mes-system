# 制造业生产管理系统 API 契约 (v1.3.0)

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
