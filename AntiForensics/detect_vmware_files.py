import os

def print_results(found, msg):
    """Print the results of the file check."""
    if found:
        print(f"[FOUND] {msg}")
    else:
        print(f"[NOT FOUND] {msg}")


def is_file_exists(path):
    """Check if a file exists at the given path."""
    return os.path.isfile(path)


def get_windows_directory():
    """Get the Windows directory path."""
    return os.environ.get('WINDIR', 'C:\\Windows')


def detect_vmware_files():
    """
    Check for VMware-related files in the System32\\drivers directory.
    """
    # Array of strings of blacklisted paths
    paths = [
        "System32\\drivers\\vmnet.sys",
        "System32\\drivers\\vmmouse.sys",
        "System32\\drivers\\vmusb.sys",
        "System32\\drivers\\vm3dmp.sys",
        "System32\\drivers\\vmci.sys",
        "System32\\drivers\\vmhgfs.sys",
        "System32\\drivers\\vmmemctl.sys",
        "System32\\drivers\\vmx86.sys",
        "System32\\drivers\\vmrawdsk.sys",
        "System32\\drivers\\vmusbmouse.sys",
        "System32\\drivers\\vmkdb.sys",
        "System32\\drivers\\vmnetuserif.sys",
        "System32\\drivers\\vmnetadapter.sys",
    ]

    # Getting Windows Directory
    win_dir = get_windows_directory()
    status = False
    # Check each file one by one
    for path in paths:
        full_path = os.path.join(win_dir, path)
        msg = f"Checking file {full_path}"
        if is_file_exists(full_path):
            print_results(True, msg)
            status = True
        else:
            print_results(False, msg)
    return status


def call_detect_vmware_files():
    """
    This tool is reliant of finding vmware driver files, if they are misplaced in the directory, there maybe false
    positives
    :return:
    """
    if detect_vmware_files():
        print("VM")
        return True
    return False
