FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3-pip

RUN mkdir /app

WORKDIR /app

COPY ./library_project/ /app
COPY ./requirements.txt /app

RUN rm /app/db.sqlite3

RUN pip3 install -r requirements.txt
RUN python3 manage.py collectstatic --no-input

RUN ./update-db.sh

ENTRYPOINT ./run-server.sh