import ctypes

def RecycleBin():
    # Access the Windows shell32 DLL
    shell32 = ctypes.windll.shell32

    # Flags (0 = show no UI, no sound, no confirmation)
    # You can also use these flags if needed:
    # SHERB_NOCONFIRMATION = 0x00000001
    # SHERB_NOPROGRESSUI = 0x00000002
    # SHERB_NOSOUND = 0x00000004
    # Example: No confirmation or progress bar
    flags = 0x00000001 | 0x00000002
    result = shell32.SHEmptyRecycleBinW(None, None, flags)


    if result == 0:
        print("Recycle Bin emptied successfully.")
    else:
        print(f"Failed to empty Recycle Bin. Error Code: {result}")

