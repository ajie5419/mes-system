#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "=== MES 系统一键部署 ==="

# 检查依赖
command -v docker >/dev/null 2>&1 || { echo "❌ 需要安装 Docker"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "❌ 需要 Docker Compose v2"; exit 1; }

# 复制 env 文件
if [ ! -f .env ]; then
    cp env.example .env
    echo "⚠️  已生成 .env，请修改 JWT_SECRET_KEY"
fi

# 构建并启动
echo "🔨 构建镜像..."
docker compose build
docker compose up -d

# 等待数据库就绪
echo "⏳ 等待数据库就绪..."
until docker compose exec db pg_isready -U mes -d mes_db >/dev/null 2>&1; do
    sleep 2
done
echo "✅ 数据库已就绪"

# 执行迁移
echo "📦 执行数据库迁移..."
docker compose exec backend alembic upgrade head 2>/dev/null || \
    docker compose exec backend python -c "from database import Base; Base.metadata.create_all(Base.metadata.bind)" 2>/dev/null || true

# 创建管理员账号
echo "👤 创建初始管理员..."
docker compose exec backend python -c "
from database import SessionLocal
from models import User
from passlib.context import CryptContext
pwd = CryptContext(schemes=['bcrypt'])
db = SessionLocal()
if not db.query(User).filter(User.username=='admin').first():
    db.add(User(username='admin', hashed_password=pwd.hash('admin123'), role='admin', full_name='管理员'))
    db.commit()
    print('管理员已创建: admin / admin123')
else:
    print('管理员已存在')
db.close()
" 2>/dev/null || echo "⚠️  管理员创建跳过（表可能未就绪）"

echo ""
echo "=== 部署完成 ==="
echo "前端: http://localhost"
echo "后端: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "默认账号: admin / admin123"
