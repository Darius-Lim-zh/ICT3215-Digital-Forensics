import os
import ctypes
from ctypes import wintypes


def is_directory_exists(path):
    """Check if a directory exists at the given path."""
    return os.path.isdir(path)


def get_program_files_directory():
    """Get the appropriate Program Files directory based on system architecture."""
    if is_wow64():
        # For 64-bit systems, return the Program Files (x86) directory
        return os.environ.get('ProgramFiles(x86)', '')  # Use this environment variable for 64-bit
    else:
        # For 32-bit systems, return the Program Files directory
        return os.environ.get('ProgramFiles', '')


def is_wow64():
    """Check if the system is running a 64-bit version of Windows."""
    # This function checks whether the current process is running under WOW64
    return ctypes.windll.kernel32.IsWow64Process(ctypes.windll.kernel32.GetCurrentProcess(),
                                                 ctypes.byref(wintypes.BOOL()))


def detect_vmware_dir():
    """Check for the existence of the 'VMWare' directory in Program Files."""
    program_files_dir = get_program_files_directory()
    target_dir = "VMWare"

    # Combine paths
    path = os.path.join(program_files_dir, target_dir)

    # Check if the directory exists
    return is_directory_exists(path)


def call_detect_vmware_dir():
    if detect_vmware_dir():
        print("VMWare directory exists.")
        return True
    else:
        print("VMWare directory does not exist.")
        return False