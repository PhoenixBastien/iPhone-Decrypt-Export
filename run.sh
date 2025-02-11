#!/bin/bash

# check for wsl interoperation file (only present in windows)
if [ -f "/proc/sys/fs/binfmt_misc/WSLInterop" ]
then # User is running WSL through Windows (pin of shame)
    # get windows env variables with cmd.exe and convert paths to wsl paths
    APPDATA=$(wslpath $(cmd.exe /c echo %APPDATA%))
    USERPROFILE=$(wslpath $(cmd.exe /c echo %USERPROFILE%))
    BACKUP_ROOT="$APPDATA/Apple Computer/MobileSync/Backup"
    EXPORT_ROOT="$USERPROFILE/Export"
else # User is a true Unix enjoyer (Mac or Linux)
    BACKUP_ROOT="$HOME/Library/Application Support/MobileSync/Backup"
    EXPORT_ROOT="$HOME/Export"
fi

# remove previous export
rm -rf $EXPORT_ROOT # for testing but should be removed
# pull docker images
docker pull python:alpine
docker pull rust:alpine
# build image and run new container from image
docker build -t imessage-decrypt-export:latest .
docker run --rm -it -v "$BACKUP_ROOT":/mnt/Backup -v "$EXPORT_ROOT":/mnt/Export \
    imessage-decrypt-export:latest