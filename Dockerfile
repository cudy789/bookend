FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3-pip python3-opencv

RUN mkdir /app

WORKDIR /app

COPY ./requirements.txt /app

RUN pip3 install -r requirements.txt

COPY ./src/ /app

RUN python3 manage.py collectstatic --no-input

RUN ./update-db.sh

ENTRYPOINT ./run-server.sh