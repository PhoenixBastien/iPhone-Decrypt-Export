from iphone_backup_decrypt import EncryptedBackup, RelativePath, RelativePathsLike

def handler(event, context):
    try:
        passphrase = 'Fall2024!'
        backup_path = 'backup/'
        backup = EncryptedBackup(backup_directory=backup_path,
                                 passphrase=passphrase)

        # Extract the SMS SQLite database and attachments
        backup.extract_file(relative_path=RelativePath.TEXT_MESSAGES,
                            output_filename='Library/SMS/sms.db')
        backup.extract_files(relative_paths_like=RelativePathsLike.SMS_ATTACHMENTS,
                             output_folder='.',
                             preserve_folders=True)

        status = 'Decryption successful'
    except:
        status = 'Decryption failed'

    return {
        'status': status
    }