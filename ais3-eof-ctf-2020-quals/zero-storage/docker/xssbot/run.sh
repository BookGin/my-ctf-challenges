#!/usr/bin/env bash

# root
python3 << EOF
import os, socket, time
while True:
  try:
    ip = socket.gethostbyname(os.getenv("WEB_SERVICE_NAME"))
    name = os.getenv("WEB_HOSTNAME")
    with open("/etc/hosts", "a") as f:
      f.write("\\n" + ip + " " + name + "\\n")
    break
  except Exception:
    print("Wait for webserver to start...")
    time.sleep(3)
EOF

# user
sudo --preserve-env --set-home --user user --group user bash << EOF
redis-server --protected-mode no &
for _ in {1..$WORKERS}; do 
  rq worker &
done
sleep infinity
EOF
