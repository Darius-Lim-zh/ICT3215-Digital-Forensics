
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
        print(f"Usage: python {os.path.basename(__file__)} <path_to_tampered_pyc_file> <xor_value>")
        sys.exit(1)

    pyc_file = sys.argv[1]
    xor_value = int(sys.argv[2], 16)

    if not os.path.isfile(pyc_file):
        print(f"Error: {pyc_file} does not exist.")
        sys.exit(1)

    load_and_execute_pyc_in_memory(pyc_file, xor_value)
    