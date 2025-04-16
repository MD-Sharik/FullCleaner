import sys
import os
from cx_Freeze import setup, Executable

# ADD FILES AND FOLDERS
include_files = [
    'icon.ico',
    'themes/',
    'images/',
    'modules/',
    'widgets/',
    'license.json',
    'session.json',
    'TempCleaning.py',
    'Temp32Cleaning.py',
    'Recycle.py',
    'Browser.py',
    'startup_manager.py',
    'registery_cleaner.py',
    'ram_booster.py',
]

# List of all module files
packages = [
    'PySide6',
    'psutil',
    'requests',
    'json',
    'os',
    'sys',
    'platform',
    'threading',
    'time'
]

build_options = {
    'packages': packages,
    'include_files': include_files,
    'excludes': [],
    'include_msvcr': True,
}

# TARGET
target = Executable(
    script="main.py",
    base="Win32GUI",
    icon="icon.ico",
    target_name="FullCleaner.exe",
    shortcut_name="FullCleaner",
    shortcut_dir="DesktopFolder"
)

# SETUP CX FREEZE
setup(
    name="FullCleaner",
    version="1.0.0",
    description="System Cleaner and Optimizer",
    options={'build_exe': build_options},
    executables=[target]
)
