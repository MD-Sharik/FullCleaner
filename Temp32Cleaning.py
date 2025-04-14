import os
import shutil


def Temp32Cleaning():
    folder = 'C:/Windows/Temp'
    deleteFileCount = 0
    deleteFolderCount = 0

    for item in os.listdir(folder):
        filePath = os.path.join(folder, item)
        itemName = os.path.basename(filePath)

        try:
            if os.path.isfile(filePath):
                os.unlink(filePath)
                print(f'{itemName} file deleted')
                deleteFileCount += 1  # FIXED: use +=, not =+
            elif os.path.isdir(filePath):
                if 'chocolatey' in filePath:
                    continue
                shutil.rmtree(filePath)
                print(f'{itemName} folder deleted')
                deleteFolderCount += 1  # FIXED: use +=, not =+
        except Exception as e:
            print(f'Access is Denied: {itemName} ({str(e)})')
    print(f'\nTotal: {deleteFileCount} files and {deleteFolderCount} folders deleted')
