#!/usr/bin/env bash

# disable directory listing
chmod 1733 /dev/shm /tmp /var/tmp

service redis-server restart
service nginx restart
rm -f /tmp/.X1-lock
Xvfb :1.0 &

# Start nginx
# service nginx restart

# Start workers
export DISPLAY=:1.0
for _ in {1..4}; do
  sudo --set-home --user user node /home/user/app/worker.js &
done

# Start web server
sudo --set-home --user user node /home/user/app/server.js
