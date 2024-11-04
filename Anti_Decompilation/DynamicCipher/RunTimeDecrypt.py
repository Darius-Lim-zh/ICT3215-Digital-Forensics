import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

def encrypt_script(input_file, key):
    # Read the script content
    with open(input_file, 'rb') as f:
        script_data = f.read()

    # Generate an initialization vector (IV)
    iv = os.urandom(16)

    # Create AES cipher with CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Padding for block cipher (AES block size is 16 bytes)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(script_data) + padder.finalize()

    # Encrypt the data
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Return both the IV and the encrypted data
    return iv, encrypted_data

def generate_decryption_script(iv, encrypted_data, key, output_file):
    # Convert key, IV, and encrypted data to byte literals
    iv_literal = repr(iv)
    encrypted_data_literal = repr(encrypted_data)
    key_literal = repr(key)

    # Template for the decryption script
    decryption_script = f'''
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

def decrypt_script(encrypted_data, iv, key):
    # Create AES cipher with CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the data
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Remove padding
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    # Return decrypted Python code
    return decrypted_data.decode('utf-8')

def execute_decrypted_script(decrypted_code):
    # Create a new dictionary for the execution context
    exec_globals = {{}}
    
    # Dynamically execute the decrypted Python code in the new context
    exec(decrypted_code, exec_globals)

    # Now you can call the functions from the executed code
    # For example, if 'main' is defined in the decrypted code, it can be called as follows:
    if 'main' in exec_globals:
        exec_globals['main']()

# Example: Replace this with your actual encryption key (must be the same as used for encryption)
key = {key_literal}

# Embedded encrypted data and IV
iv = {iv_literal}  # 16 bytes IV (Initialization Vector)
encrypted_data = {encrypted_data_literal}  # This is the encrypted code

# Decrypt and execute the code
decrypted_code = decrypt_script(encrypted_data, iv, key)
execute_decrypted_script(decrypted_code)
'''

    # output_path = os.path.join('..', '..', 'Output', os.path.basename(output_file))
    output_path = os.path.join('Output', os.path.basename(output_file))

    # Write the decryption script with embedded encrypted code to the output file
    with open(output_path, 'w') as f:
        f.write(decryption_script)

    print(f"Decryption script generated and saved to {output_path}")

    return output_path


# To be used in UI
def runtime_decrypt(input_file):
    key = os.urandom(32)
    base_name = input_file.split('/')[-1]
    output_file = f"{input_file.split(base_name)[0]}runtimedecrypt_{base_name}"

    # output_file = f"runtimedecrypt_{input_file}"

    # Encrypt the input script
    iv, encrypted_data = encrypt_script(input_file, key)

    # Generate the decryption script with embedded encrypted data
    output_path = generate_decryption_script(iv, encrypted_data, key, output_file)
    folder_path = input_file.split('/')[:-2]
    final_output = folder_path + "/" + output_path

    # print(f"Decryption script generated and saved to {output_file}")
    return final_output

def main():
    # Input Python file to be encrypted
    input_file = 'test.py'  # Replace with your actual script path
    # output_file = 'runtimedecrypt_script.py'  # The final Python script with embedded encrypted data

    runtime_decrypt(input_file)


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

if __name__ == '__main__':
    main()
