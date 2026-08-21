#!/bin/bash
set -e

echo "Starting application..."

# 等待数据库就绪（如果使用外部数据库，可以调整连接逻辑）
if [ -n "$DB_URI" ]; then
    echo "Waiting for database to be ready..."
    # 这里可以添加数据库连接检查逻辑
fi

# 如果需要自动运行数据库迁移
if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

# 启动应用
echo "Starting uvicorn server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
