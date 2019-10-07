#!/usr/bin/env bash

default_bind="127.0.0.1:8080"

if [ "$1" == "unixsocket" ]; then
  default_bind="unix:sock/server.sock"
fi

gunicorn \
  --bind "$default_bind" \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 1 \
  --umask 007 \
  main:server
