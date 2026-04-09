# MES 制造业生产管理系统

制造业执行系统（Manufacturing Execution System），用于管理生产工单、进度跟踪、变更记录、质量管控等核心业务。

## 技术栈

- **后端**: Python FastAPI + SQLAlchemy + PostgreSQL
- **前端**: Vue 3 + Element Plus + Vite
- **部署**: Docker Compose / Nginx

## 功能模块

- 工单管理（创建、分配、跟踪）
- 生产进度汇报
- 变更记录与确认
- 里程碑管理
- 质量问题跟踪
- 供应商管理
- 图纸管理
- 文件上传
- 用户权限与审计日志

## 快速开始（本地开发）

```bash
# 后端
cd backend
pip install -r requirements.txt
DATABASE_URL=sqlite:///./mes.db python -c "from database import Base, engine; Base.metadata.create_all(engine)"
bash start.sh

# 前端
cd frontend
npm install
npm run dev
```

访问 http://localhost:8000/docs 查看 API 文档。

## 部署

详见 [deploy/README.md](deploy/README.md)

## 项目结构

```
mes-system/
├── backend/          # FastAPI 后端
│   ├── main.py       # 入口
│   ├── config.py     # 配置
│   ├── database.py   # 数据库
│   ├── models/       # 数据模型
│   ├── routers/      # API 路由
│   ├── migrations/   # Alembic 迁移
│   └── alembic.ini
├── frontend/         # Vue3 前端
│   └── src/
├── deploy/           # 部署配置
│   ├── docker-compose.yml
│   ├── nginx.conf
│   ├── backend/Dockerfile
│   └── scripts/deploy.sh
└── README.md
```
