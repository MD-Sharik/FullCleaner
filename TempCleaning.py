import os
import shutil


def TempCleaning():
    folder = 'C:/Users/'+os.getlogin()+'/AppData/Local/Temp'
    deleteFileCount = 0
    deleteFolderCount = 0
    for files in os.listdir(folder):
        filePath = os.path.join(folder,files)
        indexNo = filePath.find('\\')
        itemName = filePath[indexNo+1:]
        try:
            if os.path.isfile(filePath):
                os.unlink(filePath)
                print('%s file deleted' % itemName)
                deleteFileCount +=1
            elif os.path.isdir(filePath):
                if filePath.__contains__('chocolatey'):continue
                shutil.rmtree(filePath)
                print('%s Folder Deleted'  % itemName)
                deleteFolderCount +=1
        except Exception as e:
            print('Access is Denied: %s' % itemName)
        print(str(deleteFileCount)+'files and '+ str(deleteFolderCount) + 'folders deleted')
    