import os


def detect_vm_driver():
    """
    Detect if the environment is a virtual machine by checking common VM artifacts.
    """
    vm_artifacts = [
        "C:\\Windows\\System32\\drivers\\vmhgfs.sys",  # VMware
        "C:\\Windows\\System32\\vboxguest.sys",  # VirtualBox
        "C:\\Windows\\System32\\drivers\\vmmouse.sys",  # VMware mouse driver
        "C:\\Windows\\System32\\drivers\\vm3dmp.sys",  # VMware 3D graphics driver
        "C:\\Windows\\System32\\Drivers\\VBoxMouse.sys",  # VirtualBox
        "C:\\Windows\\System32\\Drivers\\VBoxGuest.sys",  # VirtualBox guest tools
        "C:\\Windows\\System32\\Drivers\\vmhgfs.sys",  # VMware shared folder driver
        "C:\\Windows\\System32\\Drivers\\vmmouse.sys",  # VMware mouse driver
        "C:\\Program Files (x86)\\VMware\\VMware Tools",  # VMware tools directory
    ]

    for artifact in vm_artifacts:
        if os.path.exists(artifact):
            print(f"Virtual Machine detected: {artifact}")
            return True
    return False


def call_detect_vm_driver():
    """
    Call the detect vm function
    :return:
    """
    if detect_vm_driver():
        print("VM detected! Terminating.")
        # exit(1)
        return True
    else:
        print("Not in vm, carry on")
        return False