#!/bin/bash

# check for wsl interoperation file (only present in windows)
if [ ! -f "/proc/sys/fs/binfmt_misc/WSLInterop" ]
then # user is a true unix enjoyer (mac or linux)
    # get local backup root path
    BACKUP_ROOT="$HOME/Library/Application Support/MobileSync/Backup"
else # user is running wsl through windows (pin of shame)
    # get windows home dir with powershell and convert to wsl path without '\r'
    HOME=$(wslpath $(powershell.exe '$HOME') | tr -d '\r')
    # get local backup root path
    BACKUP_ROOT="$HOME/AppData/Roaming/Apple Computer/MobileSync/Backup"
fi

# get local export root path
EXPORT_ROOT="$HOME/Export"
# remove previous export (for testing but should be removed)
rm -rf $EXPORT_ROOT

# pull docker images
docker pull python:alpine
docker pull rust:alpine

# build image and run container with mounted backup and export volumes
docker build -t imessage-decrypt-export:latest .
docker run --rm -it -v "$BACKUP_ROOT":/mnt/Backup -v "$EXPORT_ROOT":/mnt/Export \
    imessage-decrypt-export:latest