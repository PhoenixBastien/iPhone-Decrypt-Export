from iphone_backup_decrypt import (
    EncryptedBackup, RelativePath, RelativePathsLike, MatchFiles
)
import subprocess
import os
import plistlib
from tabulate import tabulate
from pwinput import pwinput
from datetime import datetime, timezone

def extract_imessage(backup: EncryptedBackup) -> None:
    '''Extract iMessage database and attachments from backup.'''
    HOME = os.getenv('HOME')
    backup.extract_files(relative_paths_like='Library/SMS/%',
                         output_folder=HOME, preserve_folders=True)
    
def extract_whatsapp(backup: EncryptedBackup) -> None:
    '''Extract WhatsApp database and attachments from backup.'''
    HOME = os.getenv('HOME')
    backup.extract_file(relative_path=RelativePath.WHATSAPP_MESSAGES,
                        output_filename=f'{HOME}/{RelativePath.WHATSAPP_MESSAGES}')
    backup.extract_file(relative_path=RelativePath.WHATSAPP_CONTACTS,
                        output_filename=f'{HOME}/{RelativePath.WHATSAPP_CONTACTS}')
    backup.extract_files(**MatchFiles.WHATSAPP_ATTACHMENTS,
                         output_folder=HOME, preserve_folders=True)

def extract_all(backup: EncryptedBackup) -> None:
    HOME = os.getenv('HOME')
    backup.extract_files(relative_paths_like=RelativePathsLike.ALL_FILES,
                         output_folder=HOME, preserve_folders=True)
    
def get_device_properties(backup_path: str) -> dict[str, str]:
    '''Read properties list file to get device info.'''
    with open(f'{backup_path}/Info.plist', 'rb') as f:
        plist = plistlib.load(f)

    keys = ['Device Name', 'Last Backup Date', 'Phone Number',
            'Product Name', 'Unique Identifier']
    return {key: plist[key] for key in keys}
    
def export_imessage(format: str, copy_method: str,
                    db_path: str,export_path: str) -> None:
    args = [
        'imessage-exporter',
        '-f', format,
        '-c', copy_method,
        '-p', db_path,
        '-o', export_path
    ]
    subprocess.run(args)

def select_device() -> tuple[str, str]:
    '''Prompt user to select device to backup.'''
    BACKUP_MOUNT = '/mnt/Backup'
    hashes = os.listdir(BACKUP_MOUNT)
        
    data = []
    for id in hashes:
        backup_path = f'{BACKUP_MOUNT}/{id}'
        row = get_device_properties(backup_path)
        data.append(row)
        
    print(tabulate([row.values() for row in data], headers=list(data[0].keys()),
                   showindex=range(1, len(hashes) + 1), tablefmt='simple_grid'))
    
    i = int(input('Enter the row index of a device ID: ')) - 1
    return data[i]['Unique Identifier'], data[i]['Device Name']

def main() -> None:
    HOME = os.getenv('HOME')
    BACKUP_MOUNT = '/mnt/Backup'
    EXPORT_MOUNT = '/mnt/Export'

    device_id, device_name = select_device()
    print(device_id, device_name)
    backup_path = f'{BACKUP_MOUNT}/{device_id}'
    password = pwinput('Enter backup password: ')

    try:
        print('Decrypting messages...')

        # decrypt iOS backup
        backup = EncryptedBackup(backup_directory=backup_path,
                                 passphrase=password)

        # # Extract iMessage database and attachments
        extract_imessage(backup)

        # Extract WhatsApp database and attachments
        # extract_whatsapp(backup)

        # Extract all files
        # extract_all(backup)

        
        print('Decryption successful!')
    except Exception as error:
        print('Decryption failed!', error)
        exit(1)
    
    try:
        print('Exporting decrypted messages...')
        
        export_imessage(
            format='html',
            copy_method='full',
            db_path=f'{HOME}/{RelativePath.TEXT_MESSAGES}',
            export_path=f'{EXPORT_MOUNT}/{device_name}/iMessage'
        )

        # export whatsapp
        # f'wtsexporter -i -d {HOME}/ChatStorage.sqlite -m {HOME}'
        
        subprocess.run('sleep infinity'.split())

        print('Export successful!')
        exit(0)
    except Exception as error:
        print('Export failed!', error)
        exit(1)

if __name__ == '__main__':
    main()