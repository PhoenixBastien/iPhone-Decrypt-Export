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
    backup.extract_files(relative_paths_like='Library/SMS/%',
                         output_folder=os.getenv('HOME'), preserve_folders=True)
    
def extract_whatsapp(backup: EncryptedBackup) -> None:
    '''Extract WhatsApp database and attachments from backup.'''
    backup.extract_file(relative_path=RelativePath.WHATSAPP_MESSAGES,
                        output_filename='ChatStorage.sqlite')
    # backup.extract_file(relative_path=RelativePath.WHATSAPP_CONTACTS,
    #                     output_filename=RelativePath.WHATSAPP_CONTACTS)
    backup.extract_files(**MatchFiles.WHATSAPP_ATTACHMENTS,
                         output_folder='Attachments', preserve_folders=True)

# def extract_all(backup: EncryptedBackup) -> None:
#     backup.extract_file(relative_path=RelativePath.SAFARI_HISTORY,
#                          output_filename='History.db')


def extract_history(backup: EncryptedBackup) -> None:
    backup.extract_file(relative_path=RelativePath.SAFARI_HISTORY,
                         output_filename='History.db')
    
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

    if len(hashes) == 0:
        print('There are no backups available.')
        quit()
        
    data = []
    for id in hashes:
        backup_path = f'{BACKUP_MOUNT}/{id}'
        row = get_device_properties(backup_path)
        data.append(row)
    
    indices = range(1, len(hashes) + 1)
    print(tabulate([row.values() for row in data], headers=list(data[0].keys()),
                   showindex=indices, tablefmt='simple_grid'))
    
    try:
        i = int(input('Enter the row index of a device ID: '))
    except ValueError:
        i = -1
        
    while i not in indices:
        i = int(input('Index not in range. Try again: '))
        
    return data[i - 1]['Unique Identifier'], data[i - 1]['Device Name']

def main() -> None:
    HOME = os.getenv('HOME')
    BACKUP_MOUNT = '/mnt/Backup'
    EXPORT_MOUNT = '/mnt/Export'
    
    device_id, device_name = select_device()
    print('You selected', device_name)
    backup_path = f'{BACKUP_MOUNT}/{device_id}'
    os.mkdir(f'{EXPORT_MOUNT}/{device_id}')
    password = pwinput('Enter backup password: ')

    # decrypt iOS backup
    backup = EncryptedBackup(backup_directory=backup_path, passphrase=password)

    try: # extract and export imessage database and attachments
        print('Extracting iMessage...')
        extract_imessage(backup)
        print('Exporting iMessage...')
        subprocess.run(f'imessage-exporter -f html -c full \
                       -p {HOME}/{RelativePath.TEXT_MESSAGES} \
                       -o {EXPORT_MOUNT}/{device_id}/iMessage'.split())
        print('Success!')
    except Exception as e:
        print('Failure!', e)

    try: # extract and export whatsapp database and attachments
        print('Extracting WhatsApp...')
        extract_whatsapp(backup)
        print('Exporting WhatsApp...')
        subprocess.run(f'wtsexporter -i -d ChatStorage.sqlite -m Attachments \
                       -o {EXPORT_MOUNT}/{device_id}/WhatsApp'.split())
        print('Success!')
    except Exception as e:
        print('Failure!', e)
    
    try: # extract and export safari history
        print('Extracting Safari history...')
        extract_history(backup)
        print('Exporting Safari history...')
        subprocess.run(f'mkdir {EXPORT_MOUNT}/Safari && \
                       cp History.db {EXPORT_MOUNT}/{device_id}/Safari'.split())
        print('Success!')
    except Exception as e:
        print('Failure!', e)

    subprocess.run('sleep infinity'.split())

if __name__ == '__main__':
    main()