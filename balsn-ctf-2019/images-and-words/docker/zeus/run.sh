#!/usr/bin/env bash

# This script will be run as root

chmod 1733 /dev/shm

service nginx restart

cd /home/zeus
sudo -H -u zeus \
  gunicorn \
  --bind unix:sock/server.sock \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 5 \
  --access-logfile - \
  --error-logfile - \
  --umask 007 \
  sandbox_main:server
