from iphone_backup_decrypt import (
    EncryptedBackup, RelativePath, RelativePathsLike, MatchFiles
)

def main():
    # backup_password = 'Canada!1'
    backup_password = input('Enter backup code: ')
    backup_path = './backup'
    try:
        print('Decrypting backup...')

        backup = EncryptedBackup(backup_directory=backup_path,
                                 passphrase=backup_password)

        # Extract the SMS SQLite database and attachments
        backup.extract_file(relative_path=RelativePath.TEXT_MESSAGES,
                            output_filename='./Library/SMS/sms.db')
        backup.extract_files(relative_paths_like=RelativePathsLike.SMS_ATTACHMENTS,
                             output_folder='.', preserve_folders=True)

        # # Extract WhatsApp SQLite database and attachments:
        # backup.extract_file(relative_path=RelativePath.WHATSAPP_MESSAGES,
        #                     output_filename="./output/whatsapp.sqlite")
        # backup.extract_files(**MatchFiles.WHATSAPP_ATTACHMENTS,
        #                     output_folder="./output/whatsapp",
        #                     preserve_folders=False)
        
        print('Decryption successful!')
    except Exception as error:
        print('Decryption failed!', error)

if __name__ == '__main__':
    main()