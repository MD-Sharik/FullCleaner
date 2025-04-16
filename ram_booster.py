import psutil
import ctypes
from ctypes import wintypes
import subprocess
import os
import sys
import tempfile

class RamBooster:
    def __init__(self):
        self._kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        self._user32 = ctypes.WinDLL('user32', use_last_error=True)
        
    def optimize_memory(self):
        """Perform memory optimization operations"""
        results = {}
        
        # 1. Terminate non-essential background processes
        terminated = self.terminate_low_priority_processes()
        results['terminated_processes'] = terminated
        
        # 2. Clear system file cache
        self.clear_system_file_cache()
        
        # 3. Run empty standby list (requires admin rights)
        self.clear_standby_list()
        
        # 4. Get memory info after optimization
        mem = psutil.virtual_memory()
        results['available_memory'] = mem.available / (1024**2)  # MB
        results['percent_free'] = 100 - mem.percent
        
        return results
    
    def terminate_low_priority_processes(self):
        """Terminate non-essential background processes that consume memory
        Returns the number of processes terminated"""
        low_priority_processes = [
            'OneDrive.exe', 'Skype.exe', 'Spotify.exe', 'Teams.exe',
            'Dropbox.exe', 'Discord.exe', 'Steam.exe', 'EpicGamesLauncher.exe',
            'slack.exe', 'chrome.exe', 'msedge.exe', 'firefox.exe',
            'AdobeIPCBroker.exe', 'AdobeNotificationClient.exe', 'CCXProcess.exe',
            'Adobe Desktop Service.exe', 'Adobe CEF Helper.exe', 'AdobeUpdateService.exe'
        ]
        
        terminated_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] in low_priority_processes:
                    proc.terminate()
                    terminated_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        return terminated_count
    
    def clear_system_file_cache(self):
        """Clear system file cache using Windows API
        Returns True if successful, False otherwise"""
        try:
            # Define necessary structures and functions
            class SYSTEM_MEMORY_LIST_COMMAND(ctypes.Structure):
                _fields_ = [("Command", wintypes.DWORD)]
                
            # System memory commands
            MemoryEmptyWorkingSets = 2
            MemoryFlushModifiedList = 3
            MemoryPurgeStandbyList = 4
            
            NtSetSystemInformation = ctypes.windll.ntdll.NtSetSystemInformation
            
            # Clear working sets (process memory)
            command = SYSTEM_MEMORY_LIST_COMMAND(MemoryEmptyWorkingSets)
            result1 = NtSetSystemInformation(80, ctypes.byref(command), ctypes.sizeof(command))
            
            # Flush modified pages
            command = SYSTEM_MEMORY_LIST_COMMAND(MemoryFlushModifiedList)
            result2 = NtSetSystemInformation(80, ctypes.byref(command), ctypes.sizeof(command))
            
            return result1 == 0 or result2 == 0
        except Exception:
            return False
    
    def clear_standby_list(self):
        """Clear standby list using administrative PowerShell commands
        Returns True if successful, False otherwise"""
        try:
            # Create a PowerShell command to clear the standby list
            # This requires admin privileges
            ps_command = """
            $MemoryInfo = [PSCustomObject]@{
                EmptyWorkingSets = 2
                ModifiedPageList = 3
                StandbyList = 4
            }
            
            $NtSetSystemInformation = @"
            [DllImport("ntdll.dll")]
            public static extern int NtSetSystemInformation(int InfoClass, IntPtr Info, int Length);
            "@
            
            $Ntdll = Add-Type -MemberDefinition $NtSetSystemInformation -Name NtDll -Namespace Win32 -PassThru
            
            # Clear standby list
            $Command = [System.Runtime.InteropServices.Marshal]::AllocHGlobal(4)
            [System.Runtime.InteropServices.Marshal]::WriteInt32($Command, $MemoryInfo.StandbyList)
            $Result = $Ntdll::NtSetSystemInformation(80, $Command, 4)
            [System.Runtime.InteropServices.Marshal]::FreeHGlobal($Command)
            
            exit $Result
            """
            
            # Write the PowerShell script to a temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.ps1', delete=False)
            temp_file_path = temp_file.name
            temp_file.write(ps_command.encode('utf-8'))
            temp_file.close()
            
            # Run the PowerShell script with elevated privileges
            command = f'powershell -NoProfile -ExecutionPolicy Bypass -File "{temp_file_path}"'
            result = subprocess.run(
                ['powershell', '-Command', f'Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File {temp_file_path}" -Verb RunAs -Wait'],
                capture_output=True, 
                text=True
            )
            
            # Clean up
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
            return result.returncode == 0
            
        except Exception:
            return False
            
    def get_memory_status(self):
        """Get current memory status
        Returns a dictionary with memory information"""
        try:
            memory = psutil.virtual_memory()
            return {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'free': memory.free,
                'percent': memory.percent
            }
        except Exception:
            return {
                'total': 0,
                'available': 0,
                'used': 0,
                'free': 0,
                'percent': 0
            }