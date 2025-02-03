#!/bin/bash

# set device hash string and set backup path from device hash string
DEVICE_HASH=00008030-001C050E0EBB802E
BACKUP_PATH="$HOME/Library/Application Support/MobileSync/Backup/$DEVICE_HASH"
# pull python docker image
docker pull python:latest
# stop all running containers and force remove all unused containers
docker stop $(docker ps -q)
docker container prune -f
# remove export dir
rm -rf export
# build image and run new container from image
docker build --build-arg DEVICE_HASH=$DEVICE_HASH -t docker-image:test .
docker run --rm -v ./bin:/home/phoenix/bin \
                -v "$BACKUP_PATH":/home/phoenix/backup \
                -v ./export:/home/phoenix/export \
                docker-image:test