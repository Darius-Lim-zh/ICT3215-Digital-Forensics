import os
import ctypes
from ctypes import wintypes

# Helper functions
def is_directory_exists(path):
    """Check if a directory exists at the given path."""
    return os.path.isdir(path)

def get_program_files_directory():
    """Get the appropriate Program Files directory based on system architecture."""
    if is_wow64():
        # For 64-bit systems, return the Program Files (x86) directory
        return os.environ.get('ProgramFiles(x86)', '')
    else:
        # For 32-bit systems, return the Program Files directory
        return os.environ.get('ProgramFiles', '')

def is_wow64():
    """Check if the system is running a 64-bit version of Windows."""
    is_wow64_process = wintypes.BOOL()
    ctypes.windll.kernel32.IsWow64Process(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(is_wow64_process))
    return is_wow64_process.value

# VM directory detection functions
def detect_vmware_dir():
    """Check for the existence of the 'VMWare' directory in Program Files."""
    program_files_dir = get_program_files_directory()
    target_dir = "VMware"
    path = os.path.join(program_files_dir, target_dir)
    return is_directory_exists(path)

def detect_virtualbox_dir():
    """Check for the existence of the 'Oracle/VirtualBox' directory in Program Files."""
    program_files_dir = get_program_files_directory()
    target_dir = os.path.join("Oracle", "VirtualBox")
    path = os.path.join(program_files_dir, target_dir)
    return is_directory_exists(path)

def detect_kvm_dir():
    """Check for directories related to KVM on Linux or Windows."""
    paths_to_check = [
        "/usr/libexec/qemu-kvm",  # KVM executable location on Linux
        "/dev/kvm",               # KVM device file
        os.path.join(get_program_files_directory(), "KVM")  # Windows KVM directory (if exists)
    ]
    return any(is_directory_exists(path) for path in paths_to_check)

def detect_hyperv_dir():
    """Check for the existence of Hyper-V related directories."""
    program_files_dir = get_program_files_directory()
    target_dir = os.path.join("Hyper-V")
    path = os.path.join(program_files_dir, target_dir)
    return is_directory_exists(path)

def detect_parallels_dir():
    """Check for the existence of Parallels related directories (mainly for macOS or Windows)."""
    program_files_dir = get_program_files_directory()
    target_dir = "Parallels"
    path = os.path.join(program_files_dir, target_dir)
    return is_directory_exists(path)

# Main function to consolidate VM checks
def call_detect_vm_dir():
    """Run all VM directory checks and return a dictionary with results."""
    vm_detected = {
        "VMware": detect_vmware_dir(),
        "VirtualBox": detect_virtualbox_dir(),
        "KVM": detect_kvm_dir(),
        "Hyper-V": detect_hyperv_dir(),
        "Parallels": detect_parallels_dir()
    }

    # Check if any VM was detected
    is_vm = any(vm_detected.values())
    if is_vm:
        print("Virtual Machine detected:", {k: v for k, v in vm_detected.items() if v})
        return True
    else:
        print("No Virtual Machine directories detected.")
        return False

    # return is_vm, vm_detected
