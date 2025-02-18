import csv
import os
import plistlib
import shlex
import shutil
import sqlite3
import subprocess
from glob import glob
from iphone_backup_decrypt import EncryptedBackup, RelativePath, DomainLike
from pwinput import pwinput
from tabulate import tabulate

def select_device() -> tuple[str, str]:
    '''Prompt user to select device to backup.'''
    # match backup path patterns
    backup_paths = glob('/mnt/Backup/' + '[0-9A-F]' * 8 + '-' + '[0-9A-F]' * 16)

    # quit if there are no backups available
    if len(backup_paths) == 0:
        print('There are no backups available!')
        quit()

    # define table headers
    headers = (
        'Device Name',
        'Last Backup Date',
        'Phone Number',
        'Product Name',
        'Unique Identifier'
    )

    # get device info for all backups
    encrypted_backups = []
    for backup_path in backup_paths:
        # skip to next iternation if not backup is not encrypted
        with open(f'{backup_path}/Manifest.plist', 'rb') as f:
            if not plistlib.load(f)['IsEncrypted']:
                continue
        
        # get device info from Info.plist
        with open(f'{backup_path}/Info.plist', 'rb') as f:
            plist = plistlib.load(f, aware_datetime=True)

        # ensure last backup date is a datetime object 
        # and convert it to string in local timezone
        dt = plist['Last Backup Date']
        assert isinstance(dt, datetime)
        plist['Last Backup Date'] = dt.astimezone().strftime(r'%Y-%m-%d %H:%M')

        # add device info to list of encrypted backups
        encrypted_backups.append([plist[header] for header in headers])
    
    # quit if there are no encrypted backups available
    if len(encrypted_backups) == 0:
        print('There are no encrypted backups available!')
        quit()
    
    # set row indices starting at 1
    indices = range(1, len(encrypted_backups) + 1)

    # print formatted table
    print(tabulate(tabular_data=encrypted_backups,
                   headers=headers,
                   showindex=indices,
                   tablefmt='simple_grid'))

    # prompt user to select backup with valid row index in range
    i = -1
    while i not in indices:
        try:
            i = int(input('Enter a row index to select an encrypted backup: '))
            if i not in indices:
                print('Index not in range!')
        except ValueError:
            print('Not a number!')
            i = -1
        
    return dict(zip(headers, encrypted_backups[i - 1]))

def export_imessage(backup: EncryptedBackup, export_path: str) -> None:
    '''Export iMessage chats to html.'''
    # extract imessage database and attachments from encrypted backup
    backup.extract_files(relative_paths_like='Library/SMS/%',
                         output_folder=os.getenv('HOME'),
                         preserve_folders=True)
    
    # export imessage data with imessage-exporter binary
    subprocess.run(shlex.split(
        f'imessage-exporter \
        --use-caller-id \
        --format html \
        --copy-method full \
        --db-path {os.getenv('HOME')}/{RelativePath.TEXT_MESSAGES} \
        --export-path {export_path}/iMessage'
    ))
    
def export_whatsapp(backup: EncryptedBackup, export_path: str) -> None:
    '''Export WhatsApp chats to html.'''
    backup.extract_files(domain_like=DomainLike.WHATSAPP,
                         output_folder='WhatsApp',
                         preserve_folders=True)
    
    # export whatsapp data with wtsexporter binary
    subprocess.run(shlex.split(
        f'wtsexporter \
        --ios \
        --move-media \
        --no-avatar \
        --db WhatsApp/ChatStorage.sqlite \
        --media WhatsApp \
        --output {export_path}/WhatsApp'
    ))

def export_history(backup: EncryptedBackup, export_path: str) -> None:
    '''Export Safari history to csv.'''
    # extract history sqlite database from encrypted backup
    backup.extract_file(relative_path=RelativePath.SAFARI_HISTORY,
                        output_filename='History.db')
    
    # select history data from sqlite database
    con = sqlite3.connect('History.db')
    cur = con.cursor()
    res = cur.execute(
        'SELECT \
            DATETIME(v.visit_time + 978307200, "unixepoch", "localtime"), \
            v.title, \
            i.url, \
            i.visit_count \
        FROM history_items AS i JOIN history_visits AS v \
        ON v.history_item = i.id \
        ORDER BY visit_time DESC'
    )

    # export history data to csv file
    with open(f'{export_path}/Safari History.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        headers = ('Visit Time', 'Title', 'URL', 'Visit Count')
        writer.writerow(headers)
        writer.writerows(res.fetchall())
        con.close()

def main() -> None:
    device_info = select_device()
    print('You selected', device_info['Device Name'])
    device_id = device_info['Unique Identifier']
    backup_path = f'/mnt/Backup/{device_id}'
    export_path = f'/mnt/Export/{device_id}'

    # remove export path directory if it already exists
    if os.path.isdir(export_path):
        shutil.rmtree(export_path)

    os.mkdir(export_path)

    password = pwinput('Enter backup password: ')
    backup = EncryptedBackup(backup_directory=backup_path, passphrase=password)

    # extract and export imessage database and attachments
    try:
        print('Exporting iMessage chats to HTML...')
        export_imessage(backup, export_path)
    except Exception as e:
        print('iMessage chat export failed!', e)
    else:
        print('iMessage chats successfully exported!')

    # extract and export whatsapp database and attachments
    try:
        print('Exporting WhatsApp chats to HTML...')
        export_whatsapp(backup, export_path)
    except Exception as e:
        print('WhatsApp chat export failed!', e)
    else:
        print('WhatsApp chats successfully exported!')
    
    # extract and export safari history
    try:
        print('Exporting Safari history to CSV...')
        export_history(backup, export_path)
    except Exception as e:
        print('Safari history export failed!', e)
    else:
        print('Safari history successfully exported!')

    # subprocess.run(shlex.split('sleep infinity'))

if __name__ == '__main__':
    main()