#!/usr/bin/env bash

# This script should be run by zeus using sudo.

set -x

name="$1"
user="$(echo "$name" | sha256sum | head -c32)"

# stop the server (sudo process)
pkill --pidfile "/home/zeus/sandbox/$name/server.pid"

# remove all the files
rm -rf "/home/zeus/sandbox/$name"

# clean all the process
pkill -9 --uid "$user"

userdel -f "$user"
groupdel -f "$user"
