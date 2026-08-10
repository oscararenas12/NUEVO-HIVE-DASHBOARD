#!/usr/bin/env sh
# Container entrypoint: wait for Postgres, then start the API.
# Phase 1 has no migrations yet -- that is added in Phase 2.
set -e

host="${POSTGRES_HOST:-api-db}"
port="${POSTGRES_PORT:-5432}"
user="${POSTGRES_USER:-postgres}"

echo "Waiting for Postgres at ${host}:${port}..."
until pg_isready -h "$host" -p "$port" -U "$user" >/dev/null 2>&1; do
  sleep 1
done
echo "Postgres is ready."

echo "Running database migrations..."
alembic upgrade head

# exec so uvicorn becomes PID 1 and receives container signals.
# --reload because compose bind-mounts the source for live editing.
exec uvicorn src.main:app --host 0.0.0.0 --port 5000 --reload
