# MES 系统开发计划

## 总则
- 每完成一个任务，同步更新 API 文档、README、CHANGELOG
- 代码规范：TypeScript 类型完整，Python type hints，中文注释
- 每批完成后本地验证通过才进入下一批

---

## 第一批：核心基建

### Task 1.1 — JWT 认证系统
**后端：**
- `backend/services/auth_service.py` — JWT 签发/验证/刷新
- `backend/routers/auth.py` — POST /api/v1/auth/login, /register, /refresh, /me
- `backend/middleware/auth.py` — Depends 注入获取当前用户
- `backend/config.py` — JWT_SECRET, TOKEN_EXPIRE 配置
- 密码 hash（bcrypt）
- 所有现有接口加 auth 依赖，未登录返回 401
- 管理员初始种子脚本

**前端：**
- `src/views/Login.vue` — 登录页
- `src/api/index.ts` — 拦截器加 token，401 跳登录
- `src/stores/auth.ts` — 用户状态管理（pinia）
- App.vue 未登录时显示登录页

**文档：** 更新 api_specs.md 认证章节

### Task 1.2 — RBAC 权限体系
**后端：**
- `backend/models/permission.py` — 权限表、角色-权限关联表
- `backend/services/permission_service.py` — 权限校验
- `backend/middleware/rbac.py` — require_permission 装饰器
- 权限粒度：模块级（work_orders:read/write, users:read/write 等）
- 各路由按权限级别控制

**前端：**
- 侧边栏菜单根据权限动态显示
- 无权限按钮隐藏或 disabled

**文档：** 更新 api_specs.md 权限章节、权限矩阵表

### Task 1.3 — 操作日志审计
**后端：**
- `backend/models/audit_log.py` — 操作日志表（user_id, action, resource, detail, ip, timestamp）
- `backend/middleware/audit.py` — 自动记录增删改操作
- `backend/routers/audit.py` — GET /api/v1/audit/logs（分页、筛选、导出）

**前端：**
- `src/views/AuditLog.vue` — 操作日志页面（筛选、分页、时间线展示）

**文档：** 更新 api_specs.md

### Task 1.4 — 文件上传（图纸管理）
**后端：**
- `backend/routers/upload.py` — POST /api/v1/upload（文件上传）
- `backend/services/file_service.py` — 文件存储（本地 /uploads 目录）
- Drawing 模型关联 file_path，支持预览
- `backend/config.py` — UPLOAD_DIR 配置

**前端：**
- DrawingList.vue — 文件上传组件、预览、版本管理
- WorkOrderDetail.vue — 关联图纸展示

**文档：** 更新 api_specs.md 文件上传章节

### Task 1.5 — PostgreSQL 迁移 + 部署脚本
- `backend/config.py` — DATABASE_URL 支持 PostgreSQL
- `backend/migrations/` — 初始化建表 SQL / Alembic 迁移
- `backend/start.sh` — 更新启动脚本
- `deploy/docker-compose.yml` — PostgreSQL + 后端 + Nginx
- `deploy/nginx.conf` — 反代配置
- `deploy/env.example` — 环境变量模板

**文档：** 部署文档、环境变量说明

---

## 第二批：业务增强

### Task 2.1 — 甘特图排程
### Task 2.2 — 消息推送（企微 Webhook）
### Task 2.3 — 数据导出 Excel
### Task 2.4 — 打印模板

---

## 第三批：体验打磨

### Task 3.1 — 前端交互升级
### Task 3.2 — 实时通知（WebSocket）
### Task 3.3 — 数据大屏

---

## 当前进度

| 任务 | 状态 | 完成时间 |
|------|------|----------|
| 1.1 JWT 认证 | ⏳ 待执行 | |
| 1.2 RBAC 权限 | ⏳ 待执行 | |
| 1.3 操作日志 | ⏳ 待执行 | |
| 1.4 文件上传 | ⏳ 待执行 | |
| 1.5 PostgreSQL + 部署 | ⏳ 待执行 | |
| 2.1 甘特图 | 🔜 第二批 | |
| 2.2 消息推送 | 🔜 第二批 | |
| 2.3 Excel 导出 | 🔜 第二批 | |
| 2.4 打印模板 | 🔜 第二批 | |
| 3.1 交互升级 | 🔜 第三批 | |
| 3.2 WebSocket | 🔜 第三批 | |
| 3.3 数据大屏 | 🔜 第三批 | |
