# # prompt user for device hash
# prompt_user(){
#     hashes=($(ls "$BACKUP_ROOT"))
#     stat "$BACKUP_ROOT/$hashes" -c %n,%.19y | sed "1i Device Hash,Modified Date\n" | column -s , -t
#     PS3="Enter a number to select backup hash: "
#     select device_hash in ${hashes[@]}
#     do
#         echo "You selected $REPLY) $device_hash"
#         break
#     done
# }

# external drive needs to be mounted
mount_drive() {
    mkdir -p /mnt/d
    sudo mount -t drvfs D: /mnt/d
    export EXPORT_ROOT="/mnt/d/Export"
}

prompt_user() {
    PS3="Enter a number to select a device ID: "
    hashes=($(ls /mnt/Backup))
    select device_hash in ${hashes[@]}
    do
        echo "You selected option $REPLY: $device_hash"
        break
    done
}

export_imessage() {
    local format=$1
    local copy_method=$2
    local db_path=$3
    local export_path=$4
    imessage-exporter -f $format -c $copy_method -p $db_path -o $export_path
}