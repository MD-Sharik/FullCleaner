import winreg
import psutil

class StartupManager:
    def __init__(self):
        self.startup_locations = [
            ('HKEY_CURRENT_USER', winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            ('HKEY_LOCAL_MACHINE', winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            ('HKEY_CURRENT_USER', winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
            ('HKEY_LOCAL_MACHINE', winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce")
        ]
        
    def get_startup_apps(self):
        """Get list of all startup applications"""
        startup_apps = []
        
        for key_name, hkey, path in self.startup_locations:
            try:
                key = winreg.OpenKey(hkey, path)
                count = winreg.QueryInfoKey(key)[1]
                
                for i in range(count):
                    name, value, _ = winreg.EnumValue(key, i)
                    startup_apps.append({
                        'name': name,
                        'command': value,
                        'registry_key_name': key_name,
                        'registry_path': path
                    })
                    
                winreg.CloseKey(key)
            except Exception as e:
                print(f"Error accessing {path}: {e}")
                
        return startup_apps
    
    def disable_startup_app(self, app_info):
        """Disable a startup application by removing it from registry"""
        try:
            # Convert key name back to handle
            if app_info['registry_key_name'] == 'HKEY_CURRENT_USER':
                hkey = winreg.HKEY_CURRENT_USER
            elif app_info['registry_key_name'] == 'HKEY_LOCAL_MACHINE':
                hkey = winreg.HKEY_LOCAL_MACHINE
            else:
                return False
                
            key = winreg.OpenKey(hkey, app_info['registry_path'], 0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, app_info['name'])
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error disabling {app_info['name']}: {e}")
            return False