from iphone_backup_decrypt import (
    EncryptedBackup, RelativePath, RelativePathsLike
)

def main():
    print('Decrypting backup...')
    try:
        passphrase = 'Fall2024!'
        backup_path = './backup'
        backup = EncryptedBackup(
            backup_directory=backup_path, passphrase=passphrase
        )
        # Extract the SMS SQLite database and attachments
        backup.extract_file(
            relative_path=RelativePath.TEXT_MESSAGES,
            output_filename='./Library/SMS/sms.db'
        )
        backup.extract_files(
            relative_paths_like=RelativePathsLike.SMS_ATTACHMENTS,
            output_folder='.', preserve_folders=True
        )
        print('Decryption successful!')
    except:
        print('Decryption failed!')

if __name__ == '__main__':
    main()