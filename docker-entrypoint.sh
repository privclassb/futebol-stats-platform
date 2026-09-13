#!/bin/sh
set -e

echo "Aplicando migrations do banco de dados..."
alembic upgrade head

exec "$@"
