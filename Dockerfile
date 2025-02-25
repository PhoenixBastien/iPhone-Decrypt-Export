# use rust:alpine as builder image
FROM rust:alpine AS builder

# install imessage-exporter binary
RUN apk update && apk add libc-dev && cargo install imessage-exporter

# use python:alpine as base image
FROM python:alpine

# keep python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# turn off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# copy imessage-exporter binary from rust image
COPY --from=builder /usr/local/cargo/bin/imessage-exporter /usr/local/bin

# install imagemagick and ffmpeg binaries for media conversions
RUN apk update && apk add ffmpeg imagemagick imagemagick-heic

# create non-root app user
RUN adduser --disabled-password --gecos "" appuser

# set working directory to app user's home directory
WORKDIR /home/appuser
COPY . .

# install pip requirements
RUN python -m pip install -r requirements.txt

# set default non-root app user
USER appuser

# set command to be executed when running container
CMD ["python", "app.py"]