#!/bin/bash

docker run -d --name=bookend --privileged \
  -v "${PWD}"/library_project/db.sqlite3:/app/db.sqlite3:rw \
  --env DJANGO_SECRET_KEY="RANDOM_SECRET_KEY_VALUE" \
  --env ALLOWED_HOST="YOUR_HOSTNAME" \
  --rm -p 8080:8080 \
  rogueraptor7/bookend:latest