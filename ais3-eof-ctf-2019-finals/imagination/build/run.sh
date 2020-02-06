#!/usr/bin/env bash
set -e
set -x

for i in {1..1}; do
  COMPOSE_PROJECT_NAME="team${i}" \
  ENC_SHADOW=`sed -n "${i}p" ./enc_shadow` \
  PORT=$[60300+${i}] \
  docker-compose up &
done
