#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"

# 数据库迁移
if [ "$1" != "--no-migrate" ]; then
    echo "执行数据库迁移..."
    alembic upgrade head 2>/dev/null || python -c "from database import Base; Base.metadata.create_all(engine)" 2>/dev/null || true
fi

nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &
echo $! > server.pid
echo "服务已启动，PID: $(cat server.pid)"
