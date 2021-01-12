#!/usr/bin/env bash
# root
chmod 1733 /tmp
nginx
gunicorn \
  --workers $WORKERS \
  --worker-class uvicorn.workers.UvicornWorker \
  --access-logfile - \
  --error-logfile - \
  --bind 127.0.0.1:8000 \
  --user user \
  --group user \
  --chdir /app \
  server:app
