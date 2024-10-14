from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def encrypt_script(input_file, output_file, key):
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

    # Write the encrypted data with the IV prepended to the output file
    with open(output_file, 'wb') as f:
        f.write(iv + encrypted_data)


def main():
    # Usage: provide 32-byte key (AES-256)
    key = os.urandom(32)
    encrypt_script('input_script.py', 'encrypted_script.enc', key)


if __name__ == '__main__':
    main()
