# Changelog

## 2026-04-09 - Task 2.3: Excel 数据导出

### 后端
- 新增 `openpyxl` 依赖
- 新增 `services/export_service.py`：工单列表、工单详情（多 Sheet）、进度汇总、审计日志、用户列表导出
- 新增 `routers/export.py`：5 个 GET 导出接口，带 RBAC 权限控制，返回 StreamingResponse
- main.py 注册 export router

### 前端
- 新增 `ExportButton.vue` 通用导出组件（支持 blob 下载、loading 状态）
- WorkOrderList / WorkOrderDetail / AuditLog / UserList 页面集成导出按钮

### 文档
- 更新 API 文档

## 2026-04-09 - Task 2.1: 甘特图排程

### 后端
- 新增 GET /api/v1/work-orders/gantt-data 接口
- 支持按工单ID筛选或查询全部进行中工单
- 返回里程碑计划/实际日期、完成率、偏差天数
- 新增 GanttMilestoneResponse、GanttWorkOrderResponse schema

### 前端
- 新增 GanttView.vue 甘特图排程页面（ECharts 自定义渲染）
- 计划时段蓝色条、实际时段绿色条、延期红色标记
- 今日线（红色虚线）、完成节点 ✅ 标记
- 支持日/周/月视图切换、工单筛选、时间轴缩放
- 鼠标悬浮显示里程碑详情
- 侧边栏新增"排程甘特图"菜单项

### 文档
- 更新 api_specs.md 添加甘特图接口

## 2026-04-09 - Task 1.5: PostgreSQL 迁移 + 部署脚本

### PostgreSQL 迁移
- 默认数据库切换为 PostgreSQL（保留 SQLite fallback）
- 新增连接池配置（pool_size=10, max_overflow=20, pre_ping）
- 添加 Alembic 迁移支持（autogenerate from SQLAlchemy models）
- 安装 psycopg2-binary、alembic 依赖

### 部署脚本
- Docker Compose 编排（PostgreSQL + Backend + Nginx）
- Nginx 反向代理配置（API、静态文件、gzip）
- Backend Dockerfile（Python 3.10-slim）
- 一键部署脚本（build → migrate → admin account）
- init.sql、env.example

### 文档
- 根目录 README.md（项目介绍、结构、快速开始）
- deploy/README.md（部署指南）
- start.sh 兼容双数据库模式

## 2026-04-09 - Task 2.2: 消息推送功能

### 后端
- 新增 Notification 模型（站内通知：用户ID、标题、内容、类型、已读状态、关联资源）
- 新增 WebhookConfig 模型（企业微信/钉钉/自定义 Webhook 配置）
- 新增 notification_service：创建/批量创建通知、分页查询、标记已读/全部已读、未读计数、删除
- 新增 webhook_service：企业微信/钉钉/通用 Webhook 发送，配置 CRUD
- 新增通知路由：GET/PUT/DELETE /api/v1/notifications 系列
- 新增 Webhook 路由：/api/v1/webhook/config CRUD + 测试发送（仅 Admin）
- 工单创建时自动通知管理员
- 变更发起时通知相关部门
- 变更全部确认时通知发起人和相关人员
- 新增 httpx 依赖

### 前端
- 新增 NotificationCenter.vue：通知列表、类型筛选、已读/未读区分、删除、关联资源跳转
- App.vue 新增通知铃铛图标（右上角 badge 显示未读数）、下拉预览面板
- 侧边栏新增"通知中心"菜单
- 新增 notification.ts Pinia store（未读数 30 秒轮询）
- api/index.ts 新增通知和 Webhook 相关接口
### v1.5.0 — Task 2.4 打印模板
- 新增 `backend/services/print_service.py`：工单打印数据、进度报告打印数据
- 新增 `backend/routers/print.py`：GET /api/v1/print/work-order/{wo_id}、GET /api/v1/print/progress-report/{wo_id}
- 新增 `frontend/src/views/PrintPreview.vue`：打印预览页面（企业级表格排版，支持 window.print()）
- 新增 `frontend/src/components/PrintButton.vue`：打印按钮组件
- 新增 `frontend/src/styles/print.css`：打印专用样式（@media print、A4 适配）
- `WorkOrderDetail.vue` 新增打印工单按钮
- `api/index.ts` 新增打印数据接口

