#!/bin/sh
set -eu

python /app/server/scripts/prepare_artifacts.py

exec "$@"
