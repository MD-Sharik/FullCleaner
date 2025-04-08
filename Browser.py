import os
import shutil

def close_browser(name_list, display_name):
    for name in name_list:
        os.system(f"taskkill /f /im {name} >nul 2>&1")
    print(f"All {display_name} windows closed.")

def clean_cache(folder, browser_name):
    deleteFileCount = 0
    deleteFolderCount = 0

    if not os.path.exists(folder):
        print(f"{browser_name} cache folder does not exist.")
        return

    for item in os.listdir(folder):
        filePath = os.path.join(folder, item)
        itemName = os.path.basename(filePath)
        try:
            if os.path.isfile(filePath):
                os.unlink(filePath)
                print(f'{itemName} file deleted')
                deleteFileCount += 1
            elif os.path.isdir(filePath):
                shutil.rmtree(filePath)
                print(f'{itemName} folder deleted')
                deleteFolderCount += 1
        except Exception as e:
            print(f'Access is Denied: {itemName} ({str(e)})')
    print(f'\nTotal: {deleteFileCount} files and {deleteFolderCount} folders deleted')

def chromeCleanup():
    username = os.getlogin()
    folder = f'C:/Users/{username}/AppData/Local/Google/Chrome/User Data/Default/Cache'
    close_browser(['chrome.exe'], 'Chrome')
    clean_cache(folder, 'Chrome')

def edgeCleanup():
    username = os.getlogin()
    folder = f'C:/Users/{username}/AppData/Local/Microsoft/Edge/User Data/Default/Cache'
    close_browser(['edge.exe', 'msedge.exe'], 'Edge')
    clean_cache(folder, 'Edge')

def firefoxCleanup():
    username = os.getlogin()
    base_folder = f'C:/Users/{username}/AppData/Local/Mozilla/Firefox/Profiles'
    if not os.path.exists(base_folder):
        print("Firefox profile folder does not exist.")
        return
    close_browser(['firefox.exe'], 'Firefox')
    for profile in os.listdir(base_folder):
        cache_folder = os.path.join(base_folder, profile, 'cache2')
        clean_cache(cache_folder, 'Firefox')

def braveCleanup():
    username = os.getlogin()
    folder = f'C:/Users/{username}/AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/Cache'
    close_browser(['brave.exe'], 'Brave')
    clean_cache(folder, 'Brave')

def operaCleanup():
    username = os.getlogin()
    folder = f'C:/Users/{username}/AppData/Local/Opera Software/Opera Stable/Cache'
    close_browser(['opera.exe'], 'Opera')
    clean_cache(folder, 'Opera')
