#!/usr/bin/env bash

# run as root
user="$1"
useradd --no-create-home --home-dir / --shell /bin/false "$user"
(sleep 1800;rm -rf "/sandbox/$user"; pkill -9 --uid "$user"; userdel -f "$user"; groupdel -f "$user") &
