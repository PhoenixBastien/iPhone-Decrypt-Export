import os
import plistlib
import shlex
import subprocess

from iphone_backup_decrypt import (EncryptedBackup, MatchFiles, RelativePath,
                                   RelativePathsLike)
from pwinput import pwinput
from tabulate import tabulate

# from datetime import datetime, timezone

def extract_imessage(backup: EncryptedBackup) -> None:
    '''Extract iMessage database and attachments from backup.'''
    backup.extract_files(relative_paths_like='Library/SMS/%',
                         output_folder=os.getenv('HOME'), preserve_folders=True)
    
def extract_whatsapp(backup: EncryptedBackup) -> None:
    '''Extract WhatsApp database and attachments from backup.'''
    backup.extract_file(relative_path=RelativePath.WHATSAPP_MESSAGES,
                        output_filename='./ChatStorage.sqlite')
    # backup.extract_file(relative_path=RelativePath.WHATSAPP_CONTACTS,
    #                     output_filename=RelativePath.WHATSAPP_CONTACTS)
    backup.extract_files(**MatchFiles.WHATSAPP_ATTACHMENTS,
                         output_folder='./Attachments', preserve_folders=True)

def extract_history(backup: EncryptedBackup) -> None:
    backup.extract_file(relative_path=RelativePath.SAFARI_HISTORY,
                         output_filename='./History.db')
    
def get_device_properties(backup_path: str) -> dict[str, str]:
    '''Read properties list file to get device info.'''
    with open(f'{backup_path}/Info.plist', 'rb') as f:
        plist = plistlib.load(f)

    keys = ['Device Name', 'Last Backup Date', 'Phone Number',
            'Product Name', 'Unique Identifier']
    return {key: plist[key] for key in keys}

def select_device() -> tuple[str, str]:
    '''Prompt user to select device to backup.'''
    hashes = os.listdir('/mnt/Backup')

    if len(hashes) == 0:
        print('There are no backups available.')
        quit()
        
    data = [
        get_device_properties(f'/mnt/Backup/{hash}')
        for hash in hashes
    ]
    
    indices = range(1, len(data) + 1)
    print(tabulate([row.values() for row in data],
                   headers=list(data[0].keys()),
                   showindex=indices,
                   tablefmt='simple_grid'))
    
    try:
        i = int(input('Enter the row index of a device ID: '))
    except ValueError:
        i = -1
        
    while i not in indices:
        i = int(input('Index not in range. Try again: '))
        
    return data[i - 1]['Unique Identifier'], data[i - 1]['Device Name']

def main() -> None:  
    device_id, device_name = select_device()
    print('You selected', device_name)
    backup_path = f'/mnt/Backup/{device_id}'
    export_path = f'/mnt/Export/{device_id}'
    os.mkdir(export_path)
    password = pwinput('Enter backup password: ')

    # decrypt iOS backup
    backup = EncryptedBackup(backup_directory=backup_path, passphrase=password)

    try: # extract and export imessage database and attachments
        print('Extracting iMessage...')
        extract_imessage(backup)
        
        print('Exporting iMessage...')
        args = shlex.split(f'imessage-exporter \
                           -f html \
                           -c full \
                           -p {os.getenv('HOME')}/{RelativePath.TEXT_MESSAGES} \
                           -o {export_path}/iMessage')
        subprocess.run(args)
    except Exception as e:
        print('Failure!', e)
    else:
        print('Success!')

    try: # extract and export whatsapp database and attachments
        print('Extracting WhatsApp...')
        extract_whatsapp(backup)

        print('Exporting WhatsApp...')
        args = shlex.split(f'wtsexporter -i \
                           -d ChatStorage.sqlite \
                           -m Attachments \
                           -o {export_path}/WhatsApp')
        subprocess.run(args)
    except Exception as e:
        print('Failure!', e)
    else:
        print('Success!')
    
    try: # extract and export safari history
        print('Extracting Safari history...')
        extract_history(backup)

        print('Exporting Safari history...')
        args = shlex.split(f'mkdir -p {export_path}/Safari && \
                           cp History.db {export_path}/Safari')
        subprocess.run(args)
    except Exception as e:
        print('Failure!', e)
    else:
        print('Success!')

    subprocess.run(shlex.split('sleep infinity'))

if __name__ == '__main__':
    main()