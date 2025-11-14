#!/bin/bash

# check for wsl interoperation file (only present in windows)
if [ ! -f "/proc/sys/fs/binfmt_misc/WSLInterop" ]
then # user is a true unix enjoyer (mac or linux)
    BACKUP_ROOT="$HOME/Library/Application Support/MobileSync/Backup"
    EXPORT_ROOT="$HOME/Export"
else # user is running wsl through windows (pin of shame)
    # get windows home dir with powershell and convert to wsl path without '\r'
    USERPROFILE=$(wslpath $(powershell.exe '$HOME') | tr -d '\r')
    BACKUP_ROOT="$USERPROFILE/AppData/Roaming/Apple Computer/MobileSync/Backup"
    EXPORT_ROOT="$USERPROFILE/Export"
fi

# build image and run container with mounted backup and export volumes
docker build --pull -t ide:latest .
docker run --rm -it -v "$BACKUP_ROOT":/mnt/Backup:ro -v "$EXPORT_ROOT":/mnt/Export ide:latest