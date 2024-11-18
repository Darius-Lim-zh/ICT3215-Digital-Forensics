import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


def encrypt_script(input_file, key):
    with open(input_file, 'rb') as f:
        script_data = f.read()

    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(script_data) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return iv, encrypted_data


def generate_decryption_script(iv, encrypted_data, key, output_file):
    iv_literal = repr(iv)
    encrypted_data_literal = repr(encrypted_data)
    key_literal = repr(key)

    decryption_script = f'''
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

def decrypt_script(encrypted_data, iv, key):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
    return decrypted_data.decode('utf-8')

def execute_decrypted_script(decrypted_code):
    exec_globals = {{}}
    exec(decrypted_code, exec_globals)
    if 'main' in exec_globals:
        exec_globals['main']()

key = {key_literal}
iv = {iv_literal}
encrypted_data = {encrypted_data_literal}
decrypted_code = decrypt_script(encrypted_data, iv, key)
execute_decrypted_script(decrypted_code)
'''

    with open(output_file, 'w') as f:
        f.write(decryption_script)

    print(f"Decryption script generated and saved to {output_file}")

    return output_file


def runtime_decrypt(input_file):
    try:
        # Find the path to the main.py script
        main_script_dir = os.path.dirname(os.path.abspath("main.py"))  # Assume main.py is always in the root

        # Create the Output directory relative to main.py
        output_dir = os.path.join(main_script_dir, 'Output')
        os.makedirs(output_dir, exist_ok=True)

        # Generate the output file name in the Output directory
        base_name = os.path.basename(input_file)
        output_file = os.path.join(output_dir, f"runtimedecrypt_{base_name}")

        # Encrypt the input script
        key = os.urandom(32)
        iv, encrypted_data = encrypt_script(input_file, key)

        # Generate the decryption script in the Output directory
        generate_decryption_script(iv, encrypted_data, key, output_file)

        return output_file
    except Exception as e:
        print(f"Error in runtime_decrypt: {e}")
        return None


# def main():
#     # Input Python file to be encrypted
#     input_file = 'test.py'  # Replace with your actual script path
#     # output_file = 'runtimedecrypt_script.py'  # The final Python script with embedded encrypted data
#
#     runtime_decrypt(input_file)

# def main():
#     # Input Python file to be encrypted
#     input_file = 'test.py'  # Replace with your actual script path
#     # output_file = 'runtimedecrypt_script.py'  # The final Python script with embedded encrypted data
#
#     runtime_decrypt(input_file)

# # Generate a 32-byte key (AES-256) or provide your own key
# key = os.urandom(32)
#
# # Encrypt the input script
# iv, encrypted_data = encrypt_script(input_file, key)
#
# # Generate the decryption script with embedded encrypted data
# generate_decryption_script(iv, encrypted_data, key, output_file)
#
# print(f"Decryption script generated and saved to {output_file}")

# if __name__ == '__main__':
#     main()
