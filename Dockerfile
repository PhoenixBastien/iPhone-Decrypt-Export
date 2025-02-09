# use rust:alpine as builder image
FROM rust:alpine AS builder

# install imessage-exporter binary
RUN apk add libc-dev && cargo install imessage-exporter

# use python:alpine as base image
FROM python:alpine

# copy imessage-exporter binary from rust image
COPY --from=builder /usr/local/cargo/bin/imessage-exporter /usr/local/bin/

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# set working directory
WORKDIR /app
COPY . /app

# Install pip requirements
RUN python -m pip install -r requirements.txt

# imagemagick and ffmpeg are required for media conversions on non-macOS
RUN apk update && apk add ffmpeg imagemagick imagemagick-heic

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden.
CMD ["python", "decrypt.py"]