#!/bin/bash
#  -v /etc/letsencrypt/live/cknutson.org-0001/cert.pem:/app/cert.pem:ro \
#  -v /etc/letsencrypt/live/cknutson.org-0001/privkey.pem:/app/privkey.pem:ro \

docker run -d --name=bookend --privileged \
  -v "${PWD}"/library_project/db.sqlite3:/app/db.sqlite3:rw \
  --rm -p 8080:8080 \
  rogueraptor7/bookend:latest