#!/bin/bash
while true; do

  docker pull rogueraptor7/bookend:latest;
  docker kill bookend;
  sleep 1;
  docker run -d --cpus="1.0" --memory="512m" --name=bookend \
    --rm -p 8080:8080 \
    --env DJANGO_SECRET_KEY="correcthorsebatterystaple" \
    --env ALLOWED_HOST="cknutson.org" \
    rogueraptor7/bookend:latest;

  sleep 15m;
  echo "restarting";
  sleep 1;

done