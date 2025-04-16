import winreg
import os

class RegistryCleaner:
    def __init__(self):
        self.registry_issues = []
        
    def scan_for_issues(self):
        """Scan registry for common issues"""
        self.registry_issues = []
        
        # Scan for invalid file extensions
        self._scan_file_extensions()
        
        # Scan for missing shared DLLs
        self._scan_shared_dlls()
        
        # Scan for broken uninstall entries
        self._scan_uninstall_entries()
        
        # Scan for broken MUI references
        self._scan_mui_cache()
        
        return self.registry_issues
    
    def fix_issues(self, issues_to_fix=None):
        """Fix registry issues that were found"""
        if issues_to_fix is None:
            issues_to_fix = range(len(self.registry_issues))
            
        fixed_count = 0
        for idx in issues_to_fix:
            if idx < 0 or idx >= len(self.registry_issues):
                continue
                
            issue = self.registry_issues[idx]
            if self._fix_issue(issue):
                fixed_count += 1
                
        return fixed_count
    
    def _scan_file_extensions(self):
        """Scan for invalid file extensions"""
        try:
            root_key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "")
            count = winreg.QueryInfoKey(root_key)[0]
            
            # Limit count to prevent potential overflow
            count = min(count, 10000)
            
            for i in range(count):
                try:
                    ext = winreg.EnumKey(root_key, i)
                    if ext.startswith('.'):
                        ext_key = winreg.OpenKey(root_key, ext)
                        default_value, _ = winreg.QueryValueEx(ext_key, "")
                        
                        if default_value:
                            # Check if the default handler exists
                            try:
                                handler_key = winreg.OpenKey(root_key, default_value)
                                winreg.CloseKey(handler_key)
                            except:
                                # Handler doesn't exist
                                self.registry_issues.append({
                                    'type': 'file_extension',
                                    'key': 'HKEY_CLASSES_ROOT',
                                    'subkey': ext,
                                    'value': default_value,
                                    'description': f"File extension {ext} points to non-existent handler {default_value}"
                                })
                        
                        winreg.CloseKey(ext_key)
                except:
                    pass
                    
            winreg.CloseKey(root_key)
        except Exception as e:
            print(f"Error scanning file extensions: {e}")
    
    def _scan_shared_dlls(self):
        """Scan for missing shared DLLs"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\SharedDLLs"
            shared_dlls_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            count = winreg.QueryInfoKey(shared_dlls_key)[1]
            
            # Limit count to prevent potential overflow
            count = min(count, 10000)
            
            for i in range(count):
                try:
                    dll_path, _, _ = winreg.EnumValue(shared_dlls_key, i)
                    if not os.path.exists(dll_path):
                        self.registry_issues.append({
                            'type': 'shared_dll',
                            'key': 'HKEY_LOCAL_MACHINE',
                            'subkey': key_path,
                            'value': dll_path,
                            'description': f"Shared DLL entry points to non-existent file: {dll_path}"
                        })
                except:
                    pass
                    
            winreg.CloseKey(shared_dlls_key)
        except Exception as e:
            print(f"Error scanning shared DLLs: {e}")
    
    def _scan_uninstall_entries(self):
        """Scan for broken uninstall entries"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall"
            uninstall_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            count = winreg.QueryInfoKey(uninstall_key)[0]
            
            # Limit count to prevent potential overflow
            count = min(count, 10000)
            
            for i in range(count):
                try:
                    app_key_name = winreg.EnumKey(uninstall_key, i)
                    app_key = winreg.OpenKey(uninstall_key, app_key_name)
                    
                    try:
                        uninstall_string, _ = winreg.QueryValueEx(app_key, "UninstallString")
                        if uninstall_string:
                            # Extract executable path
                            if uninstall_string.startswith('"'):
                                exe_path = uninstall_string.split('"')[1]
                            else:
                                exe_path = uninstall_string.split(' ')[0]
                                
                            if not os.path.exists(exe_path):
                                self.registry_issues.append({
                                    'type': 'uninstall',
                                    'key': 'HKEY_LOCAL_MACHINE',
                                    'subkey': f"{key_path}\\{app_key_name}",
                                    'value': 'UninstallString',
                                    'description': f"Uninstall entry points to non-existent file: {exe_path}"
                                })
                    except:
                        pass
                        
                    winreg.CloseKey(app_key)
                except:
                    pass
                    
            winreg.CloseKey(uninstall_key)
        except Exception as e:
            print(f"Error scanning uninstall entries: {e}")
    
    def _scan_mui_cache(self):
        """Scan for broken MUI cache entries"""
        try:
            key_path = r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache"
            mui_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
            count = winreg.QueryInfoKey(mui_key)[1]
            
            # Limit count to prevent potential overflow
            count = min(count, 10000)
            
            for i in range(count):
                try:
                    value_name, _, _ = winreg.EnumValue(mui_key, i)
                    if value_name.endswith('.FriendlyAppName') or value_name.endswith('.ApplicationCompany'):
                        exe_path = value_name.split('.')[0]
                        if not os.path.exists(exe_path) and os.path.splitext(exe_path)[1].lower() == '.exe':
                            self.registry_issues.append({
                                'type': 'mui_cache',
                                'key': 'HKEY_CURRENT_USER',
                                'subkey': key_path,
                                'value': value_name,
                                'description': f"MUI cache entry points to non-existent file: {exe_path}"
                            })
                except:
                    pass
                    
            winreg.CloseKey(mui_key)
        except Exception as e:
            print(f"Error scanning MUI cache: {e}")
    
    def _fix_issue(self, issue):
        """Fix a specific registry issue"""
        try:
            if issue['type'] in ['file_extension', 'shared_dll', 'uninstall', 'mui_cache']:
                # Open the key
                if issue['key'] == 'HKEY_CLASSES_ROOT':
                    root_key = winreg.HKEY_CLASSES_ROOT
                elif issue['key'] == 'HKEY_LOCAL_MACHINE':
                    root_key = winreg.HKEY_LOCAL_MACHINE
                elif issue['key'] == 'HKEY_CURRENT_USER':
                    root_key = winreg.HKEY_CURRENT_USER
                else:
                    return False
                    
                # Different handling for different issue types
                if issue['type'] == 'file_extension':
                    key = winreg.OpenKey(root_key, issue['subkey'], 0, winreg.KEY_WRITE)
                    winreg.DeleteValue(key, "")
                    winreg.CloseKey(key)
                elif issue['type'] == 'shared_dll':
                    key = winreg.OpenKey(root_key, issue['subkey'], 0, winreg.KEY_WRITE)
                    winreg.DeleteValue(key, issue['value'])
                    winreg.CloseKey(key)
                elif issue['type'] == 'uninstall':
                    # Just delete the UninstallString value, not the whole key
                    key = winreg.OpenKey(root_key, issue['subkey'], 0, winreg.KEY_WRITE)
                    winreg.DeleteValue(key, 'UninstallString')
                    winreg.CloseKey(key)
                elif issue['type'] == 'mui_cache':
                    key = winreg.OpenKey(root_key, issue['subkey'], 0, winreg.KEY_WRITE)
                    winreg.DeleteValue(key, issue['value'])
                    winreg.CloseKey(key)
                    
                return True
        except Exception as e:
            print(f"Error fixing issue: {e}")
            
        return False