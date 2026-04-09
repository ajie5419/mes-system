# CHANGELOG

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
