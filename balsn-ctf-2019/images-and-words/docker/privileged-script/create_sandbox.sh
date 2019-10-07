#!/usr/bin/env bash

# This script should be run by zeus using sudo.

set -ex

name="$1"
user="$(echo "$name" | sha256sum | head -c32)"

useradd --no-create-home --home-dir / --shell /bin/false  "$user"
usermod --append -G "$user" www-data

# nginx needs to reload, else it will get permission denied error
nginx -s reload

cd /home/zeus
# The whole directory is owned by root
cp -r app_scaffold "sandbox/$name"
# png upload directory should be fully writable by the user
mkdir "sandbox/$name/png"
chown "$user:$user" "sandbox/$name/png"
chmod 700 "sandbox/$name/png"
# so user can create unix socket
chown "$user:$user" "sandbox/$name/sock"

cd "/home/zeus/sandbox/$name"
sudo -H -u "$user" \
  bash run.sh unixsocket \
  &>/dev/null &

echo "$!" > server.pid
