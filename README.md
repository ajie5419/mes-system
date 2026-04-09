# MES 智造系统

制造业生产管理系统（MES/ERP），覆盖工单全生命周期管理、质量追溯、组织架构、审批流转、数据分析等核心场景。

## 功能列表

### 📋 工单管理
- 工单 CRUD、状态流转（Backlog → InProgress → Blocked → Completed → Archived）
- 里程碑管理、甘特图排程
- 变更控制与确认
- 进度汇报与日报
- 工单协作（多部门分配）
- 工单模板

### 🏢 组织架构
- 部门树形管理（增删改查）
- 用户管理（含角色分配）
- 角色管理

### 🔐 权限与安全
- JWT 认证（登录/注册/刷新）
- RBAC 权限体系（模块级粒度）
- 操作日志审计

### ✅ 质量管理
- 不合格品项管理
- 供应商管理
- 图纸版本管理

### 📊 数据分析
- KPI 仪表盘
- 工单趋势、周期分析、准时率、超期统计
- 部门工作量与效率分析
- 异常趋势与分类统计
- 里程碑完成率

### 📋 任务看板
- 部门任务看板（拖拽排序）
- 任务流转（待处理 → 进行中 → 已完成）

### 🔄 审批流
- 审批流程配置
- 发起审批、审批/驳回
- 审批历史记录

### ⚠️ 异常管理
- 异常上报、处理、升级、关闭
- 异常统计

### 🔔 通知中心
- 站内通知（WebSocket 实时推送）
- 通知已读/全部已读

### 🤖 自动化规则
- 工单状态变更自动触发通知
- 规则 CRUD、启用/禁用
- 执行日志

### 💬 评论系统
- 工单评论（多资源类型通用）

### 🖨️ 打印与导出
- 工单打印模板、进度报告打印
- 数据导出 Excel

### 📺 数据大屏
- 生产概况可视化大屏

### ⚙️ 系统管理
- 系统配置（分组管理）
- Webhook 配置与测试
- 文件上传管理

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic |
| 前端 | Vue 3, Element Plus, Pinia, ECharts, Vite |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） |
| 认证 | JWT (python-jose) |
| 实时通信 | WebSocket |

## 项目结构

```
mes-system/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── constants.py         # 常量定义
│   ├── models/              # SQLAlchemy 模型
│   ├── schemas/             # Pydantic 请求/响应模型
│   ├── routers/             # API 路由（25 个模块）
│   ├── services/            # 业务逻辑层
│   ├── middleware/           # 中间件（RBAC、审计）
│   ├── migrations/          # Alembic 迁移
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/           # 页面组件（25 个）
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── api/             # API 封装
│   │   └── App.vue          # 主布局与路由
│   └── package.json
├── docs/
│   └── api_specs.md
├── deploy/                  # 部署配置
├── DEVELOPMENT_PLAN.md
└── README.md
```

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
PYTHONPATH="$PWD" python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

默认账号：`admin` / `admin123`

## API 文档

启动后端后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

详细 API 规格见 [docs/api_specs.md](docs/api_specs.md)。

## 部署

见 [deploy/](deploy/) 目录：
- `docker-compose.yml` — Docker 部署
- `nginx.conf` — Nginx 反代配置
- `env.example` — 环境变量模板

## 系统截图

> 截图待补充

## 代码量

- 后端 Python: ~6,200 行
- 前端 Vue/TS: ~5,800 行
- 总计: ~12,000 行
- API 路由: 115 个
