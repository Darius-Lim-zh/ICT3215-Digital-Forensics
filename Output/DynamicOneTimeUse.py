import marshal
import sys
import os
import tkinter as tk
from tkinter import messagebox


def secure_delete(file_path=os.path.realpath(__file__), passes=1):
    """
    Securely delete the file by overwriting it with random data before deletion.

    :param file_path: Path to the file to be securely deleted.
    :param passes: Number of times to overwrite the file (default is 1).
    """
    try:
        file_size = os.path.getsize(file_path)
        with open(file_path, 'r+b') as file:
            for _ in range(passes):
                file.seek(0)
                file.write(os.urandom(file_size))
        os.remove(file_path)
        print(f'{file_path} securely deleted.')
    except Exception as e:
        print(f'Error: {e}')


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


def xor_magic_number(bytecode, xor_value):
    magic_number = bytecode[:4]
    restored_magic = bytes([(b ^ xor_value) for b in magic_number])
    return restored_magic + bytecode[4:]


def load_and_execute_pyc_in_memory(pyc_file, xor_value):
    with open(pyc_file, 'rb') as f:
        bytecode = f.read()
    restored_bytecode = xor_magic_number(bytecode, xor_value)
    code_object = marshal.loads(restored_bytecode[16:])
    globals_dict = globals()
    exec(code_object, globals_dict, globals_dict)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(
            f'Usage: python {os.path.basename(__file__)} <path_to_tampered_pyc_file> <xor_value>'
            )
        sys.exit(1)
    pyc_file = sys.argv[1]
    xor_value = int(sys.argv[2], 16)
    if not os.path.isfile(pyc_file):
        print(f'Error: {pyc_file} does not exist.')
        sys.exit(1)
    load_and_execute_pyc_in_memory(pyc_file, xor_value)
    secure_delete()
