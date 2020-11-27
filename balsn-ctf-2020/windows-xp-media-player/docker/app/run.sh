#!/usr/bin/env bash

# disable directory listing
chmod 1733 /dev/shm /tmp /var/tmp
service nginx restart

# move flag
R0=`head -c16 /dev/urandom | sha256sum | head -c32`
R1=`head -c16 /dev/urandom | sha256sum | head -c32`
if [[ -f "/flag/flag" ]]; then
  mkdir -p "/flag/$R0"
  mv /flag/flag "/flag/$R0/$R1"
fi

# create a sample playlist
mkdir -p /sandbox/Sunset_Rollercoaster/JINJI_KIKKO 
touch /sandbox/Sunset_Rollercoaster/JINJI_KIKKO/Burgundy_Red

# create secret key
head -c32 /dev/urandom > /root/key
chmod 400 /root/key
(sleep 20; rm -rf /root/key) &

# throttle db
mkdir /ips
chmod 700 /ips

cd /app
uvicorn --access-log \
  --workers 8 \
  --host 127.0.0.1 \
  --port 8000 \
  server:app
