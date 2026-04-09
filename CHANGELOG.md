# Changelog

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
