#!/bin/bash
while true; do

  docker pull rogueraptor7/bookend:latest;

  docker run -d --cpus="1.0" --memory="512m" --name=bookend \
    --rm -p 8080:8080 \
    rogueraptor7/bookend:latest;

  sleep 15m;
  docker kill bookend;
  sleep 1;
  echo "restarting";
  sleep 1;


done