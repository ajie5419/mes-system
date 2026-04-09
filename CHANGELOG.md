# CHANGELOG

## v1.7.0 (2026-04-10)

### 多部门协同功能 (Task 4.2)

#### 后端
- 新增 models/work_order_assignee.py — WorkOrderAssignee 模型
- 新增 models/department_task.py — DepartmentTask 模型
- 新增 models/approval.py — ApprovalFlow / ApprovalInstance / ApprovalStep 模型
- 新增 models/exception.py — Exception 模型
- 新增 services/task_board_service.py — 任务看板 CRUD
- 新增 services/approval_service.py — 审批流服务
- 新增 services/exception_service.py — 异常管理服务
- 新增 routers/task_board.py — 6 个端点
- 新增 routers/approvals.py — 7 个端点
- 新增 routers/exceptions.py — 7 个端点
- 修改 work_orders.py — 协作人员端点

#### 前端
- 新增 TaskBoard.vue — Kanban 看板
- 新增 ApprovalCenter.vue — 审批中心
- 新增 ExceptionCenter.vue — 异常管理（含 ECharts 趋势图）
- 新增 CollaborationView.vue — 协作面板
- 修改 App.vue — 新增 4 个菜单
- 修改 api/index.ts — 新增全部 API

## v1.6.0 (2026-04-10)

### 代码质量重构 — 消除硬编码、统一配置管理 (Task 4.1)

#### 后端
- 新增 `models/system_config.py` — SystemConfig 模型（数据库驱动配置）
- 新增 `models/department.py` — Department 模型（支持树形层级）
- 新增 `models/role.py` — Role 模型（系统预置角色管理）
- 新增 `models/work_order_template.py` — WorkOrderTemplate / MilestoneTemplate 模型
- 新增 `services/config_service.py` — 配置 CRUD + 初始化默认配置
- 新增 `services/department_service.py` — 部门树/CRUD + 初始化8个默认部门
- 新增 `services/role_service.py` — 角色 CRUD + 初始化 Admin/Manager/Worker
- 新增 `services/template_service.py` — 模板 CRUD + 初始化默认17节点模板
- 新增 `services/state_machine.py` — 工单状态机（状态流转规则化 + 审计日志）
- 新增 `routers/departments.py` — 部门管理 API（树形列表/增删改）
- 新增 `routers/system_config.py` — 系统配置 API（分组查询/批量更新）
- 新增 `routers/templates.py` — 工单模板 API（列表/详情）
- 修改 `change_service.py` — 通知部门从数据库配置获取，fallback 常量
- 修改 `work_order_service.py` — 默认里程碑从模板获取，fallback 常量
- 修改 `schemas/change_record.py` — notify_departments 改为 Optional
- `constants.py` 枚举保留作为 fallback，向后兼容

#### 前端
- 新增 `views/SystemConfig.vue` — 系统配置管理页面（分组 Tab + 批量保存）
- 新增 `views/DepartmentManage.vue` — 部门管理（树形表格 + 增删改）
- 新增 `views/TemplateManage.vue` — 工单模板管理（列表 + 节点详情弹窗）
- `api/index.ts` 新增部门/配置/模板相关 API
- `App.vue` 管理员菜单新增「系统设置」子菜单（系统配置/部门管理/工单模板）

---

## v1.3.0 (2026-04-09)

### 数据大屏 (Task 3.3)

#### 后端
- 新增 `services/bigscreen_service.py` — 大屏数据聚合查询（复用现有模型）
- 新增 `routers/bigscreen.py` — GET `/api/v1/bigscreen/overview` 接口（需 dashboard:read 权限）
- `main.py` 注册 bigscreen router

#### 前端
- 新增 `views/BigScreen.vue` — 全屏数据驾驶舱（深色科技风格）
  - 6 个指标卡（工单总数/进行中/已完成/延期/今日新增/今日完工）
  - 工单状态环形图、近 7 天趋势双线图、健康度仪表盘
  - 部门柱状图、优先级饼图、操作日志滚动列表
  - 底部延期预警滚动条
  - 实时时钟、60 秒自动刷新
- 新增 `styles/bigscreen.css` — 大屏专用样式（发光边框、入场动画、滚动动画）
- `api/index.ts` 新增 `getBigscreenOverview` API
- `App.vue` 侧边栏新增"数据大屏"菜单项，点击后全屏展示

#### 文档
- `docs/api_specs.md` 新增数据大屏接口说明

---

## v1.2.0 (2026-04-09)

### WebSocket 实时通知 (Task 3.2)

#### 后端
- 新增 `services/ws_service.py` — WebSocket 连接管理器（多设备支持、按用户/角色/全局广播、心跳超时检测）
- 新增 `routers/ws.py` — WebSocket 端点 `/api/v1/ws/notifications`（token 认证、心跳、自动断开）
- `notification_service.create_notification` 创建通知时自动通过 WebSocket 推送

#### 前端
- 新增 `composables/useWebSocket.ts` — WebSocket 连接管理（指数退避重连、心跳、状态管理）
- `stores/notification.ts` 改为 WebSocket 实时推送，断线时 fallback 到 30 秒轮询
- `App.vue` 新增 WebSocket 连接状态指示器（绿/黄/红圆点）

#### 文档
- `docs/api_specs.md` 新增 WebSocket 章节说明

---

## v1.1.0 (2026-04-09)

### 前端交互升级 (Task 3.1)

#### 全局优化
- 新增 `src/composables/useLoading.ts` — 全局 loading 管理
- 新增 `src/composables/useConfirm.ts` — 统一确认弹窗封装 (useConfirm / confirmDelete)
- 所有删除操作统一使用确认弹窗，禁止直接删除

#### 表格升级 (WorkOrderList.vue)
- 支持列排序 (点击表头 sortable="custom")
- 行点击高亮 (highlight-current-row)
- 表格密度切换 (紧凑/默认/宽松)
- 键盘快捷键: Ctrl+F 搜索聚焦, Esc 清空筛选

#### 批量操作 (WorkOrderList.vue)
- 表格新增 checkbox 列
- 批量状态变更 (选中多工单 → 批量修改状态)
- 批量导出 CSV (选中工单导出)

#### 工单详情增强 (WorkOrderDetail.vue)
- 里程碑节点支持拖拽排序修改顺序
- 里程碑支持在线编辑 (点击编辑按钮弹出弹窗: 修改计划日期、备注)
- 进度汇报区域增加内联手动汇报表单 (无需弹窗)
- 工单状态流转按钮组 (Backlog → InProgress → Completed → Archived)
- 关联信息面板: 变更记录、质量问题、操作日志三个标签页

#### Dashboard 增强 (Dashboard.vue)
- 添加「最近更新」区域 (最近 5 条操作日志)
- 指标卡片加趋势箭头 (和上次对比)
- 响应式布局适配 (移动端可用, 2列/1列自适应)

#### 全局搜索 (App.vue)
- 顶部搜索框: 输入关键词全局搜索工单 (跨工单号、项目名、客户名)
- 搜索结果下拉展示, 点击跳转工单详情
- Ctrl+K 快捷键聚焦搜索框

## v1.8.0 (2026-04-10)

### 状态管理与工作流自动化 (Task 4.3)

**状态机增强**
- 新增状态：Draft、PendingReview、Approved、OnHold、Closed、Rejected
- 完整的状态流转规则（含前置条件检查、自动动作、通知触发）
- 状态变更历史记录（StatusTransition 模型）
- transition_order_status 返回详细结果

**自动化工作流引擎**
- AutomationRule 模型（触发条件 + 动作参数，JSON配置）
- 6条内置默认规则：延期预警、延期升级、严重异常、进度停滞、完成通知、里程碑触发
- 支持触发类型：status_change / exception_created / due_date_approaching / progress_stalled
- 支持动作类型：send_notification / create_task / escalate / change_status / assign_department
- 执行日志记录

**评论与讨论系统**
- 通用评论组件（支持工单、异常、审批等多处复用）
- 树形回复结构、@提及、内部备注标记
- 提及用户自动通知

**工单时间线**
- 聚合状态变更、进度汇报、评论、变更记录、审批、异常、审计日志
- 时间轴展示组件

**前端**
- AutomationRules 页面（规则管理 + 执行日志）
- CommentPanel 通用评论组件
- Timeline 时间线组件
- WorkOrderDetail 集成评论和时间线
- 侧边栏新增"自动化规则"菜单

## [1.6.0] - 2026-04-10

### 数据分析与报表 (Task 4.4)

**后端**
- 新增 `analytics_service.py`：工单/部门/异常/进度/KPI 共 12 个分析函数
- 新增 `analytics` router：13 个 GET 端点，支持时间范围、分组维度参数
- `main.py` 注册 analytics router

**前端**
- 新增 `AnalyticsDashboard.vue`：KPI 卡片 + 8 组 ECharts 图表
- 新增 `ReportCenter.vue`：预设报表卡片 + 预览弹窗 + 导出入口
- `App.vue` 侧边栏新增"数据分析"和"报表中心"菜单
- `api/index.ts` 新增 13 个分析 API 函数
