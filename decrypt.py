from iphone_backup_decrypt import (
    EncryptedBackup, RelativePath, RelativePathsLike, MatchFiles
)
import subprocess
import os.path
import plistlib

def main():
    HOME = os.path.expanduser('~')
    device_hash = input('Enter device hash: ') or '00008030-001C050E0EBB802E' # TODO
    passphrase = input('Enter backup password: ') or 'Fall2024!' or 'Canada!1'
    backup_path = f'/app/Backup/{device_hash}'

    with open(f'{backup_path}/Info.plist', 'rb') as f:
        plist = plistlib.load(f)
        keys = ['Device Name', 'Last Backup Date', 'Phone Number', 'Product Name', 'Unique Identifier']
        data = {
            key: plist[key] for key in keys
        }
        print(data)

    try:
        print('Decrypting messages...')

        backup = EncryptedBackup(backup_directory=backup_path,
                                 passphrase=passphrase)

        # Extract SMS SQLite database and attachments
        backup.extract_file(relative_path=RelativePath.TEXT_MESSAGES,
                            output_filename=f'{HOME}/Library/SMS/sms.db')
        backup.extract_files(relative_paths_like=RelativePathsLike.SMS_ATTACHMENTS,
                             output_folder=HOME, preserve_folders=True)

        # # Extract WhatsApp SQLite database and attachments:
        # backup.extract_file(relative_path=RelativePath.WHATSAPP_MESSAGES,
        #                     output_filename="./output/whatsapp.sqlite")
        # backup.extract_files(**MatchFiles.WHATSAPP_ATTACHMENTS,
        #                     output_folder="./output/whatsapp",
        #                     preserve_folders=False)
        
        print('Decryption successful!')
    except Exception as error:
        print('Decryption failed!', error)
        exit(1)
    
    try:
        print('Exporting decrypted messages...')

        args = f'''imessage-exporter -f html -c full
                    -p {HOME}/Library/SMS/sms.db
                    -o /app/Export/{device_hash}'''.split()
        
        subprocess.run(args)
        subprocess.run('sleep infinity'.split())

        print('Export successful!')
        exit(0)
    except Exception as error:
        print('Export failed!', error)
        exit(1)

if __name__ == '__main__':
    main()