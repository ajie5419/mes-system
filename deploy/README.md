# MES 部署指南

## 环境要求

- Docker + Docker Compose v2
- 或手动部署：Python 3.10+, Node.js 18+, PostgreSQL 16+

## Docker Compose 一键部署

```bash
cd deploy
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

## 手动部署

### 后端
```bash
cd backend
pip install -r requirements.txt
export DATABASE_URL=postgresql://mes:mes123@localhost:5432/mes_db
alembic upgrade head
bash start.sh
```

### 前端
```bash
cd frontend
npm install
npm run build
# 用 nginx 托管 dist/
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | PostgreSQL 连接串 | postgresql://mes:mes123@localhost:5432/mes_db |
| JWT_SECRET_KEY | JWT 签名密钥 | mes_jwt_dev_secret_key... |
| UPLOAD_DIR | 上传文件目录 | ./uploads |

## 数据库迁移

```bash
cd backend
alembic revision --autogenerate -m "描述"
alembic upgrade head
alembic downgrade -1
```

## 常见问题

**Q: 连接数据库失败**
检查 PostgreSQL 是否运行，用户名密码是否匹配。

**Q: 迁移脚本报错**
确保 `PYTHONPATH=backend/` 并已安装所有依赖。

**Q: SQLite 兼容**
设置 `DATABASE_URL=sqlite:///./mes.db` 可回退到 SQLite 模式。
