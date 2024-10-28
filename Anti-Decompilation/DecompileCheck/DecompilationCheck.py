import py_compile
import os
import sys
import shutil


def generate_dynamic_loader(pyc_file, xor_value):
    loader_script = f"""
import marshal
import sys
import os

def xor_magic_number(bytecode, xor_value):
    magic_number = bytecode[:4]
    restored_magic = bytes([b ^ xor_value for b in magic_number])
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
        print(f"Usage: python {{os.path.basename(__file__)}} <path_to_tampered_pyc_file> <xor_value>")
        sys.exit(1)

    pyc_file = sys.argv[1]
    xor_value = int(sys.argv[2], 16)

    if not os.path.isfile(pyc_file):
        print(f"Error: {{pyc_file}} does not exist.")
        sys.exit(1)

    load_and_execute_pyc_in_memory(pyc_file, xor_value)
    """

    output_path = os.path.join('..', '..', 'Output', 'dynamic_loader.py')

    with open(output_path, 'w') as f:
        f.write(loader_script)

    print(f"Generated dynamic_loader.py to run {pyc_file} with XOR value {hex(xor_value)}.")

    print(f"dynamic_loader.py created at {output_path}")

    print(f"Sample: python dynamic_loader.py {pyc_file} {hex(xor_value)}")


def tamper_magic_number(pyc_file, xor_value):
    """
    Alters the magic number of a .pyc file by XORing it with a given value.

    Args:
        pyc_file (str): Path to the .pyc file to be tampered with.
        xor_value (int): The value to XOR the magic number with (default is 0xFF).
    """
    magic_number_len = 4
    with open(pyc_file, 'rb') as f:
        bytecode = f.read()

    if len(bytecode) < magic_number_len:
        print("Error: The .pyc file is too short to contain a magic number.")
        return

    # Display original magic number for reference
    original_magic = bytecode[:magic_number_len]
    print(f"Original magic number: {original_magic.hex()}")

    # XOR each byte of the magic number with the provided xor_value
    tampered_magic = bytes([b ^ xor_value for b in original_magic])
    print(f"Tampered magic number: {tampered_magic.hex()}")

    # Construct the tampered bytecode
    tampered_bytecode = tampered_magic + bytecode[4:]

    # Moving to Output folder
    output_path = os.path.join('..', '..', 'Output', os.path.basename(pyc_file))

    # Write the tampered bytecode back to the .pyc file
    with open(output_path, 'wb') as f:
        f.write(tampered_bytecode)

    print(f"Successfully tampered with the magic number of '{pyc_file}'.")

    print(f"XOR value used: {xor_value}")
    print(f"Magic number length: {magic_number_len}")

def compile_and_tamper(source_script, pyc_file, xor_value):
    """
    Compiles a Python script to a .pyc file and tampers with its magic number.

    Args:
        source_script (str): Path to the Python (.py) script to compile.
        pyc_file (str): Path where the compiled .pyc file will be saved.
        xor_value (hex): Hex value used for XOR of magic number
    """
    if not os.path.isfile(source_script):
        print(f"Error: The file '{source_script}' does not exist.")
        sys.exit(1)

    # Compile the Python script to a .pyc file
    try:
        py_compile.compile(source_script, cfile=pyc_file, doraise=True)
        print(f"Compiled '{source_script}' to '{pyc_file}'.")
    except py_compile.PyCompileError as e:
        print(f"Compilation failed: {e.msg}")
        sys.exit(1)

    # Tamper with the magic number of the compiled .pyc file
    tamper_magic_number(pyc_file, xor_value)

    generate_dynamic_loader(pyc_file, xor_value)


# For use in UI
def decompile_check(source_script, pyc_file, xor_value=0xFF):
    compile_and_tamper(source_script, pyc_file, xor_value)

    print("NOTE: The .pyc won't appear on intelliJ or visual studios as the magic number is not recognized")


def main():
    # Get the directory where this script is located
    # script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the paths for 'browse_annoying_site.py' and 'test.pyc'
    # source_script = os.path.join(script_dir, 'browse_annoying_site.py')
    # pyc_file = os.path.join(script_dir, 'test.pyc')
    #
    # print(source_script)
    # print(pyc_file)
    source_script = 'test.py'
    pyc_file = 'test.pyc'

    print("Starting compilation and tampering process...")

    compile_and_tamper(source_script, pyc_file, 0xff)

    print("Process completed successfully.")

if __name__ == '__main__':
    main()
