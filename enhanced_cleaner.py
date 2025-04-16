import os
import shutil
import tempfile
import subprocess

class EnhancedCleaner:
    def __init__(self):
        self.temp_locations = [
            os.path.expanduser('~\\AppData\\Local\\Temp'),
            tempfile.gettempdir(),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\INetCache'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\WER'),
            os.path.expanduser('~\\AppData\\Local\\Microsoft\\Windows\\Temporary Internet Files'),
            os.path.expanduser('~\\AppData\\Local\\CrashDumps'),
            os.environ.get('SYSTEMROOT') + '\\Temp',
            os.environ.get('SYSTEMROOT') + '\\Logs',
        ]
        
    def clear_browser_data(self):
        """Clear browser caches and history"""
        browsers = {
            'chrome': os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache'),
            'firefox': os.path.expanduser('~\\AppData\\Local\\Mozilla\\Firefox\\Profiles'),
            'edge': os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache'),
        }
        
        cleaned_bytes = 0
        for browser, path in browsers.items():
            if os.path.exists(path):
                cleaned_bytes += self._delete_dir_contents(path)
                
        return cleaned_bytes
    
    def clear_windows_temp(self):
        """Clear Windows temporary files"""
        cleaned_bytes = 0
        for location in self.temp_locations:
            if os.path.exists(location):
                cleaned_bytes += self._delete_dir_contents(location)
                
        return cleaned_bytes
    
    def clear_windows_update_cache(self):
        """Clear Windows Update cached files"""
        update_cache = os.environ.get('SYSTEMROOT') + '\\SoftwareDistribution\\Download'
        if os.path.exists(update_cache):
            # Stop Windows Update service
            subprocess.run(['net', 'stop', 'wuauserv'], shell=True)
            
            # Delete files
            cleaned_bytes = self._delete_dir_contents(update_cache)
            
            # Restart Windows Update service
            subprocess.run(['net', 'start', 'wuauserv'], shell=True)
            return cleaned_bytes
        return 0
    
    def _delete_dir_contents(self, directory):
        """Delete contents of a directory and return bytes cleaned"""
        total_bytes = 0
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            try:
                if os.path.isfile(path):
                    total_bytes += os.path.getsize(path)
                    os.unlink(path)
                elif os.path.isdir(path):
                    total_bytes += self._delete_dir_contents(path)
                    shutil.rmtree(path, ignore_errors=True)
            except Exception as e:
                print(f"Error deleting {path}: {e}")
                
        return total_bytes