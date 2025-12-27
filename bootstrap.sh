#!/bin/bash
set -euo pipefail

# detect container engine
if command -v podman >/dev/null && command -v podman-compose >/dev/null; then
    ENGINE="podman"
elif command -v docker >/dev/null && command -v docker-compose >/dev/null; then
    ENGINE="docker"
else
    echo "Error: Neither Docker nor Podman is installed."
    exit 1
fi

# check for wsl interop file (only present in windows)
if [[ -f "/proc/sys/fs/binfmt_misc/WSLInterop" ]]; then
    # user is using wsl through windows (pin of shame)
    USERPROFILE=$(wslpath "$(wslvar USERPROFILE)")
    BACKUP_ROOT="$USERPROFILE/AppData/Roaming/Apple Computer/MobileSync/Backup"
    EXPORT_ROOT="$USERPROFILE/Export"
elif [[ "$OSTYPE" = "darwin"* ]]; then
    # user is using macos
    BACKUP_ROOT="$HOME/Library/Application Support/MobileSync/Backup"
    EXPORT_ROOT="$HOME/Export"
else
    # user is likely using linux
    echo "Other operating systems not supported."
    exit 1
fi

# run compose
$ENGINE compose up --build
