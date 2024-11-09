import os
import platform
import ctypes
import time
import sys
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
        # Get the file size
        file_size = os.path.getsize(file_path)

        # Overwrite the file with random data
        with open(file_path, "r+b") as file:
            for _ in range(passes):
                file.seek(0)
                file.write(os.urandom(file_size))  # Overwrite with random data

        # Finally, delete the file
        os.remove(file_path)
        print(f"{file_path} securely deleted.")

        # Clear system memory cache after file deletion
        clear_system_cache()

    except Exception as e:
        print(f"Error: {e}")


def clear_system_cache():
    """
    Clear the system's memory cache to minimize traces in memory.
    Uses OS-specific commands.
    """
    try:
        os_type = platform.system()
        if os_type == "Linux":
            # Clear cache on Linux by dropping caches
            os.system("sync; echo 3 > /proc/sys/vm/drop_caches")
            print("Linux system memory cache cleared.")
        elif os_type == "Windows":
            # Use ctypes to force Windows system cache cleanup
            ctypes.windll.kernel32.SetSystemFileCacheSize(0, 0, 0)
            ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1)
            print("Windows system memory cache cleared.")
        else:
            print(f"Cache clearing not supported for OS: {os_type}")

        # Allow time for cache to fully clear
        time.sleep(1)

    except Exception as e:
        print(f"Error clearing system cache: {e}")


def on_close(root):
    """
    Function to be called when the popup is closed.
    """
    # Get the current script path
    script_path = os.path.realpath(__file__)

    # Securely delete the script file
    secure_delete(script_path, passes=3)  # Overwrite the file 3 times before deletion

    # Exit the application
    root.destroy()


def dest_poc_main():
    # Create a simple GUI with tkinter
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Show a popup message box
    messagebox.showinfo("Hello", "Hello, this script will delete itself after you close this message.")

    # Trigger the on_close function when the popup is closed
    root.after(0, on_close, root)

    # Run the tkinter event loop
    root.mainloop()


# if __name__ == "__main__":
def call_main():
    sys.exit(int(dest_poc_main() or 0))
