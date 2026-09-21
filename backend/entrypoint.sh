#!/bin/sh
# Запуск backend у контейнері:
#   1) чекаємо, доки база почне відповідати;
#   2) накочуємо міграції;
#   3) за потреби наповнюємо базу тестовими даними;
#   4) стартуємо сервер.
#
# Таблиці створюються лише міграціями - жодного create_all під час старту.
set -e

echo "Очікую PostgreSQL..."
python <<'PY'
import os
import sys
import time

import psycopg

dsn = os.environ.get("DATABASE_URL", "")
# psycopg не розуміє префікс SQLAlchemy "+psycopg".
dsn = dsn.replace("postgresql+psycopg://", "postgresql://")

for attempt in range(60):
    try:
        with psycopg.connect(dsn, connect_timeout=3):
            print("PostgreSQL готовий.")
            sys.exit(0)
    except Exception as exc:  # noqa: BLE001
        print(f"  спроба {attempt + 1}/60: {exc.__class__.__name__}")
        time.sleep(2)

print("PostgreSQL не відповів вчасно.", file=sys.stderr)
sys.exit(1)
PY

echo "Накочую міграції..."
alembic upgrade head

if [ "${SEED_ON_START:-true}" = "true" ]; then
    echo "Завантажую тестові дані..."
    python -m scripts.seed
fi

echo "Стартую сервер..."
exec "$@"
