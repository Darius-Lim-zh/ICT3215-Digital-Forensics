import sys
import base64
import binascii
from PyPDF2 import PdfReader
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding as sym_padding

def load_private_key(private_key_path):
    with open(private_key_path, "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=None)

def decrypt_with_aes(encrypted_data, key):
    # Extract IV from the start of the encrypted data
    iv = encrypted_data[:16]
    encrypted_content = encrypted_data[16:]
    
    # Initialize AES cipher
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt and unpad the data
    padded_data = decryptor.update(encrypted_content) + decryptor.finalize()
    unpadder = sym_padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    
    return data

def decrypt_content(encrypted_aes_key, encrypted_content, private_key):
    # Decrypt AES key using RSA private key
    aes_key = private_key.decrypt(
        base64.b64decode(encrypted_aes_key),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Decrypt the content using the AES key
    encrypted_data = base64.b64decode(encrypted_content)
    return decrypt_with_aes(encrypted_data, aes_key)

def extract_python_from_multiple_pdfs(pdf_paths, private_key_path, output_python_file_path):
    # Load private key
    private_key = load_private_key(private_key_path)

    # Initialize placeholders
    encrypted_content_parts = []
    encrypted_aes_key = None

    # Extract encrypted parts and AES key from PDFs
    for i, pdf_path in enumerate(pdf_paths):
        pdf_reader = PdfReader(pdf_path)
        metadata = pdf_reader.metadata

        # Retrieve the encrypted part and the AES key (from the first PDF)
        encrypted_part_hex = metadata.get('/EncryptedPythonFilePart')
        if encrypted_part_hex:
            encrypted_part = binascii.unhexlify(encrypted_part_hex)
            encrypted_content_parts.append(encrypted_part)
            print(f"Extracted part from {pdf_path}")
        else:
            print(f"No embedded Python file part found in {pdf_path}")

        # Retrieve the AES key from the first PDF only
        if i == 0:
            encrypted_aes_key = metadata.get('/EncryptedAESKey')
            if not encrypted_aes_key:
                print("Error: Encrypted AES key not found in the first PDF.")
                sys.exit(1)

    # Combine all parts of the encrypted content
    combined_encrypted_content = b''.join(encrypted_content_parts)

    # Decrypt and reassemble the original Python file content
    python_file_content = decrypt_content(encrypted_aes_key, combined_encrypted_content, private_key)

    # Write the reassembled content to the output Python file
    with open(output_python_file_path, 'wb') as f:
        f.write(python_file_content)

    print(f"Reassembled Python file saved to {output_python_file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python extract_rsa.py <private_key.pem> <pdf_file_1> <pdf_file_2> ... <pdf_file_n> <output_python_file>")
        sys.exit(1)

    private_key_path = sys.argv[1]
    pdf_files = sys.argv[2:-1]
    output_python_file = sys.argv[-1]

    extract_python_from_multiple_pdfs(pdf_files, private_key_path, output_python_file)
