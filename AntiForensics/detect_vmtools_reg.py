import winreg


def print_results(found, msg):
    """Print the results of the registry check for debugging only."""
    if found:
        print(f"[FOUND] {msg}")
    else:
        print(f"[NOT FOUND] {msg}")


def is_reg_key_exists(hkey, subkey):
    """Check if a registry key exists."""
    try:
        winreg.OpenKey(hkey, subkey)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error checking registry key: {e}")
        return False


def detect_vmtools_reg():
    """Check against VMware registry keys."""
    # Array of strings of blacklisted registry keys
    keys = [
        "SOFTWARE\\VMware, Inc.\\VMware Tools",
    ]
    for key in keys:
        msg = f"Checking reg key {key}"
        if is_reg_key_exists(winreg.HKEY_LOCAL_MACHINE, key):
            print_results(True, msg)
        else:
            print_results(False, msg)


def call_detect_vmtools_reg():
    if detect_vmtools_reg():
        # If even a single one of these are true, the machine is a vm
        return True
    return False
