#!/bin/bash

# set device hash string, local backup path and local export path
DEVICE_HASH=00008101-000D49980121001E
# USERNAME=$(cmd.exe /c echo %USERNAME%)
# USERPROFILE=$(wslpath "C:/Users/$USERNAME")

if [ -f "/proc/sys/fs/binfmt_misc/WSLInterop" ]
then # Windows
    echo "User is running WSL through Windows."
    # convert windows paths to wsl paths
    USERNAME=PS_ENG
    LOCAL_BACKUP_PATH=$(wslpath "C:/Users/$USERNAME/AppData/Roaming/Apple Computer/MobileSync/Backup/$DEVICE_HASH")
    LOCAL_EXPORT_PATH=$(wslpath "C:/Users/$USERNAME/Downloads/export")
else # Mac
    echo "User is a true Unix enjoyer."
    LOCAL_BACKUP_PATH="$HOME/Library/Application Support/MobileSync/Backup/$DEVICE_HASH"
    LOCAL_EXPORT_PATH="$HOME/Downloads/export"
fi
#TODO
# stat $LOCAL_BACKUP_PATH -c "%n,%.19y" | sed '1i Device Hash,Modified Date\n' | column -s, -t
# su -
# mkdir -p /mnt/d
# sudo mount -t drvfs D: /mnt/d
# LOCAL_EXPORT_PATH=/mnt/d/export # usb key
#####
rm -rf $LOCAL_EXPORT_PATH
# pull python docker image
docker pull python:latest
# stop all running containers and force remove all unused containers
# docker stop $(docker ps -q)
docker container prune -f
# build image and run new container from image
docker build --build-arg USER=$USER -t imessage-image:test .
docker run --rm -it --name imessage-container \
    -v ./bin:/home/$USER/bin \
    -v "$LOCAL_BACKUP_PATH":/home/$USER/backup \
    -v "$LOCAL_EXPORT_PATH":/home/$USER/export \
    imessage-image:test