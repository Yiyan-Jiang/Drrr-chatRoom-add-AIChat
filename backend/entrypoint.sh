#!/bin/sh
set -e

echo "==> Running normal_system migrations..."
alembic -c normal_system/alembic.ini upgrade head

echo "==> Starting backend..."
exec uvicorn main:socketio_app --host 0.0.0.0 --port 8000 --reload
