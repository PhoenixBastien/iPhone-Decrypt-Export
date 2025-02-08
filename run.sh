#!/bin/bash

# check for wsl interoperation file (only present in windows)
if [ -f "/proc/sys/fs/binfmt_misc/WSLInterop" ]
then # User is running WSL through Windows (pin of shame)
    # os=windows
    # get windows username by calling command prompt
    windows_user=$(cmd.exe /c echo %USERNAME%)
    # convert windows paths to wsl paths
    appdata=$(wslpath $(cmd.exe /c echo %appdata%))
    userprofile=$(wslpath $(cmd.exe /c echo %userprofile%))
    backup_root_path="$appdata/Apple Computer/MobileSync/Backup"
    export_root_path="$userprofile/Export"
else # User is a true Unix enjoyer (Mac or Linux)
    # os=unix
    backup_root_path="$HOME/Library/Application Support/MobileSync/Backup"
    export_root_path="$HOME/Export"
fi

# prompt user for device hash
# hashes=($(ls "$backup_root_path"))
# stat "$backup_root_path/$hashes" -c %n,%.19y | sed "1i Device Hash,Modified Date\n" | column -s , -t
# PS3="Enter a number to select backup hash: "
# select device_hash in ${hashes[@]}
# do
#     echo "You selected option $REPLY: $device_hash"
#     break
# done

# external drive needs to be mounted
# mkdir -p /mnt/d
# sudo mount -t drvfs D: /mnt/d
# export_root_path=/mnt/d/export

# remove previous export
rm -rf $export_root_path # for testing but should be removed
# pull docker images
docker pull python:alpine
docker pull rust:alpine
# build image and run new container from image
docker build -t imessage-image:test .
docker run --rm -it --name imessage-container \
    -v "$backup_root_path":/app/Backup -v "$export_root_path":/app/Export \
    imessage-image:test