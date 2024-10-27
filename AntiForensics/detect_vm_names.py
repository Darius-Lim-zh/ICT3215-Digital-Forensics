import platform
import subprocess
import cpuinfo


def detect_vm_cpuid():
    info = cpuinfo.get_cpu_info()

    # Check for hypervisor information in CPU info
    if 'hypervisor' in info['flags']:
        print("Hypervisor detected (indicates a VM).")
        return True

    return False


def call_detect_vm_cpuid():
    if detect_vm_cpuid():
        print("Detected a virtual machine.")
        return True
    else:
        print("Not running in a virtual machine.")
        return False
