import os
import sys
import tkinter as tk
from tkinter import messagebox


def secure_delete(file_path=os.path.realpath(__file__), passes=1):
    """
    Securely delete the file by overwriting it with random data before deletion.

    :param file_path: Path to the file to be securely deleted.
    :param passes: Number of times to overwrite the file (default is 1).
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

    except Exception as e:
        print(f"Error: {e}")


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

