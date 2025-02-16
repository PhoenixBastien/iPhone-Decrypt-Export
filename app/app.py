import csv
import os
import plistlib
import shlex
import sqlite3
import subprocess
from glob import glob
from iphone_backup_decrypt import EncryptedBackup, MatchFiles, RelativePath
from pwinput import pwinput
from tabulate import tabulate

def get_device_info(backup_path: str) -> dict[str, str]:
    '''Read properties list file to get device info.'''
    with open(f'{backup_path}/Info.plist', 'rb') as f:
        info_plist = plistlib.load(f, aware_datetime=True)

    # check if backup is encrypted
    with open(f'{backup_path}/Manifest.plist', 'rb') as f:
        is_encrypted = plistlib.load(f)['IsEncrypted']

    return (
        info_plist['Device Name'],
        info_plist['Last Backup Date'],
        info_plist['Phone Number'],
        info_plist['Product Name'],
        info_plist['Unique Identifier'],
        is_encrypted
    )

def select_device() -> tuple[str, str]:
    '''Prompt user to select device to backup.'''
    backup_paths = glob('/mnt/Backup/' + '[0-9A-F]' * 8 + '-' + '[0-9A-F]' * 16)

    if len(backup_paths) == 0:
        print('There are no backups available!')
        quit()
        
    data = [get_device_info(backup_path) for backup_path in backup_paths]
    headers = (
        'Device Name',
        'Last Backup Date',
        'Phone Number',
        'Product Name',
        'Unique Identifier',
        'Is Encrypted?'
    )
    indices = range(1, len(data) + 1)
    print(tabulate(tabular_data=data,
                   headers=headers,
                   showindex=indices,
                   tablefmt='simple_grid'))
    
    try:
        i = int(input('Enter a row index to select a device backup: '))
    except ValueError:
        i = -1
        
    while i not in indices:
        i = int(input('Index not in range! Try again: '))
        
    return dict(zip(headers, data[i - 1]))

def extract_imessage(backup: EncryptedBackup) -> None:
    '''Extract iMessage database and attachments from encrypted backup.'''
    backup.extract_files(relative_paths_like='Library/SMS/%',
                         output_folder=os.getenv('HOME'), preserve_folders=True)
    
def extract_whatsapp(backup: EncryptedBackup) -> None:
    '''Extract WhatsApp database and attachments from encrypted backup.'''
    backup.extract_file(relative_path=RelativePath.WHATSAPP_MESSAGES,
                        output_filename='./ChatStorage.sqlite')
    backup.extract_files(**MatchFiles.WHATSAPP_ATTACHMENTS,
                         output_folder='./Attachments', preserve_folders=True)

def extract_history(backup: EncryptedBackup) -> None:
    '''Extract Safari history from encrypted backup.'''
    backup.extract_file(relative_path=RelativePath.SAFARI_HISTORY,
                         output_filename='./History.db')

def export_history(export_path: str) -> None:
    '''Export Safari history to CSV.'''
    con = sqlite3.connect('History.db')
    cur = con.cursor()
    res = cur.execute(
        'SELECT \
            DATETIME(v.visit_time + 978307200, "unixepoch", "localtime"), \
            v.title, \
            i.url, \
            i.visit_count \
        FROM history_items AS i JOIN history_visits AS v \
        ON v.history_item = i.id'
    )

    with open(f'{export_path}/Safari History.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(('Visit Time', 'Title', 'URL', 'Visit Count'))
        writer.writerows(res.fetchall())
        
    con.close()

def main() -> None:  
    device_info = select_device()
    print('You selected', device_info['Device Name'])

    if not device_info['Is Encrypted?']:
        print('Device backup is not encrypted!')
        quit()

    device_id = device_info['Unique Identifier']
    backup_path = f'/mnt/Backup/{device_id}'
    export_path = f'/mnt/Export/{device_id}'
    os.mkdir(export_path)

    password = pwinput('Enter backup password: ')
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
        export_history(export_path=export_path)
    except Exception as e:
        print('Failure!', e)
    else:
        print('Success!')

    # subprocess.run(shlex.split('sleep infinity'))

if __name__ == '__main__':
    main()