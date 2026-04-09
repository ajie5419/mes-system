#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd)"
nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &
echo $! > server.pid
echo "服务已启动，PID: $(cat server.pid)"
