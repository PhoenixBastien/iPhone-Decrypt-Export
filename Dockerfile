# use rust:alpine as builder image
FROM rust:alpine AS builder

# install imessage-exporter binary
RUN apk update && apk add libc-dev
RUN cargo install imessage-exporter

# use python:alpine as base image
FROM python:alpine

# set python-related environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install imagemagick and ffmpeg binaries for media conversions
RUN apk update && apk add ffmpeg imagemagick imagemagick-heic

# create non-root app user
RUN adduser -D -h /home/appuser appuser

# set working directory to app user's home directory
WORKDIR /home/appuser

# install python dependencies
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# copy application code
COPY . .

# copy imessage-exporter binary from rust image
COPY --from=builder /usr/local/cargo/bin/imessage-exporter /usr/local/bin

# set default non-root app user
USER appuser

# set command to be executed when running container
CMD ["python", "app.py"]
