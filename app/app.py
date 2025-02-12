from iphone_backup_decrypt import (
    EncryptedBackup, RelativePath, RelativePathsLike, MatchFiles
)
import subprocess
import os
import plistlib
import pandas as pd

def extract_imessage(backup: EncryptedBackup) -> None:
    '''Extract iMessage database and attachments from backup.'''
    HOME = os.getenv('HOME')
    backup.extract_file(relative_path=RelativePath.TEXT_MESSAGES,
                        output_filename=f'{HOME}/Library/SMS/sms.db')
    backup.extract_files(relative_paths_like=RelativePathsLike.SMS_ATTACHMENTS,
                         output_folder=HOME, preserve_folders=True)
    
def extract_whatsapp(backup: EncryptedBackup) -> None:
    '''Extract WhatsApp database and attachments from backup.'''
    HOME = os.getenv('HOME')
    backup.extract_file(relative_path=RelativePath.WHATSAPP_MESSAGES,
                        output_filename=f'{HOME}/WhatsApp/ChatStorage.sqlite')
    backup.extract_files(**MatchFiles.WHATSAPP_ATTACHMENTS,
                         output_folder=HOME, preserve_folders=True)
    
def get_device_properties(backup_path: str) -> dict[str, str]:
    '''Read properties list file to get device info.'''
    with open(f'{backup_path}/Info.plist', 'rb') as f:
        plist = plistlib.load(f)
        return {
            key: plist[key] for key in [
                'Device Name',
                'Last Backup Date',
                'Phone Number',
                'Product Name',
                'Unique Identifier'
            ]
        }
    
def export_imessage(format: str, copy_method: str, db_path: str, export_path: str) -> None:
    args = f'imessage-exporter -f {format} -c {copy_method} -p {db_path} -o {export_path}'.split()
    subprocess.run(args)

# TODO
def prompt_user():
    backup_root = '/home/phoenix/Library/Application Support/MobileSync/Backup'
    hashes = os.listdir(backup_root)
    df = pd.DataFrame(columns=[
        'Device Name',
        'Last Backup Date',
        'Phone Number',
        'Product Name',
        'Unique Identifier'
    ])
    for i, hash in enumerate(hashes):
        backup_path = f'{backup_root}/{hash}'
        row = get_device_properties(backup_path)
        print(i, row)
        df.loc[i] = row

def main():
    HOME = os.getenv('HOME')

    # hashes = {
    #     os.listdir('/mnt/Backup')
    # }
    # device_hash = input('Enter device hash: ') # TODO
    device_hash = '00008030-001C050E0EBB802E'
    backup_path = f'/mnt/Backup/{device_hash}'
    # device_properties = get_device_properties(backup_path)
    # password = input('Enter backup password: ')
    password = 'Fall2024!' or 'Canada!1'

    try:
        print('Decrypting messages...')

        # decrypt iOS backup
        backup = EncryptedBackup(backup_directory=backup_path,
                                 passphrase=password)
        # backup = EncryptedBackup(backup_directory='/mnt/Backup/00008030-001C050E0EBB802E',
        #                          passphrase='Fall2024!')

        # Extract iMessage database and attachments
        extract_imessage(backup)

        # # Extract WhatsApp database and attachments
        # extract_whatsapp(backup)
        
        print('Decryption successful!')
    except Exception as error:
        print('Decryption failed!', error)
        exit(1)
    
    try:
        print('Exporting decrypted messages...')
        
        # export_imessage(format='html',
        #                 copy_method='full',
        #                 db_path=f'{HOME}/Library/SMS/sms.db',
        #                 export_path=f'/mnt/Export/test')

        args = f'''imessage-exporter -f html -c full
                    -p {HOME}/Library/SMS/sms.db
                    -o /mnt/Export/{device_hash}'''.split()
        
        subprocess.run(args)
        subprocess.run('sleep infinity'.split())

        print('Export successful!')
        exit(0)
    except Exception as error:
        print('Export failed!', error)
        exit(1)

if __name__ == '__main__':
    main()