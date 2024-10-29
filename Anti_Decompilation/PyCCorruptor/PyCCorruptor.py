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

    # output_path = os.path.join('..', '..','Output', 'dynamic_loader.py')
    output_path = os.path.join('Output', 'dynamic_loader.py')

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
    output_path = os.path.join('Output', os.path.basename(pyc_file))

    # Write the tampered bytecode back to the .pyc file
    with open(output_path, 'wb') as f:
        f.write(tampered_bytecode)

    print(f"Successfully tampered with the magic number of '{pyc_file}'.")

    print(f"XOR value used: {xor_value}")
    print(f"Magic number length: {magic_number_len}")


def get_next_available_filename(base_name, directory="Output"):
    """
    Generates the next available file name with an incremented counter in the specified directory.

    Args:
        base_name (str): Base name of the file (e.g., "OutputCorrupted").
        directory (str): Directory where the file will be saved.

    Returns:
        str: The next available file name with path.
    """
    counter = 1
    while True:
        filename = f"{base_name}{counter}.pyc"
        file_path = os.path.join(directory, filename)
        if not os.path.exists(file_path):
            return file_path
        counter += 1


def compile_and_tamper(source_script, xor_value):
    """
    Compiles a Python script to a .pyc file in the Output directory and tampers with its magic number.

    Args:
        source_script (str): Path to the Python (.py) script to compile.
        xor_value (hex): Hex value used for XOR of magic number
    """
    try:
        # Check if the source script exists
        if not os.path.isfile(source_script):
            print(f"Error: The file '{source_script}' does not exist.")
            return False, ""

        # Ensure the Output directory exists
        output_dir = "Output"
        os.makedirs(output_dir, exist_ok=True)

        # Get the next available file path in the Output directory
        pyc_file = get_next_available_filename("OutputCorrupted", output_dir)

        # Compile the Python script to a .pyc file
        try:
            py_compile.compile(source_script, cfile=pyc_file, doraise=True)
            print(f"Compiled '{source_script}' to '{pyc_file}'.")
        except py_compile.PyCompileError as e:
            print(f"Compilation failed: {e.msg}")
            return False, ""

        # Tamper with the magic number of the compiled .pyc file
        tamper_magic_number(pyc_file, xor_value)

        # Generate a dynamic loader if needed
        generate_dynamic_loader(pyc_file, xor_value)

        return True, pyc_file
    except Exception as e:
        print(f"Error: {e}")
        return False, ""


# Wrapper function for the UI to handle the decompile check with corruption
def pyc_corrupt_source_with_xor(source_script, xor_value=0xFF):
    return compile_and_tamper(source_script, xor_value)



