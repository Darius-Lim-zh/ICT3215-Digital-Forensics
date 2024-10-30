import os
import sys
import base64
from PyPDF2 import PdfReader, PdfWriter
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding as sym_padding
import secrets

def load_public_key(public_key_path):
    with open(public_key_path, "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())

def encrypt_with_aes(data, key):
    iv = secrets.token_bytes(16)  # 16 bytes IV for AES-128
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad the data to be AES block size compatible
    padder = sym_padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted_data  # Prepend IV to encrypted data for later use

def encrypt_content(content, public_key):
    # Generate a random 256-bit AES key for symmetric encryption
    aes_key = secrets.token_bytes(32)
    encrypted_data = encrypt_with_aes(content, aes_key)

    # Encrypt the AES key with RSA
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return base64.b64encode(encrypted_aes_key).decode('utf-8'), base64.b64encode(encrypted_data).decode('utf-8')


def split_content(content, num_parts):
    part_size = len(content) // num_parts
    return [content[i * part_size: (i + 1) * part_size] for i in range(num_parts - 1)] + [content[(num_parts - 1) * part_size:]]


def embed_python_in_multiple_pdfs(python_file_path, pdf_paths, public_key_path):
    # Load public key
    public_key = load_public_key(public_key_path)

    # Read and encrypt Python file content
    with open(python_file_path, 'rb') as f:
        python_file_content = f.read()
    encrypted_aes_key, encrypted_content = encrypt_content(python_file_content, public_key)

    # Split encrypted content into parts based on the number of PDF files
    content_parts = split_content(encrypted_content.encode(), len(pdf_paths))

    # Create output folder if it doesn’t exist
    output_folder = 'Embedded Files'
    os.makedirs(output_folder, exist_ok=True)

    # Embed each part in a PDF
    for i, pdf_path in enumerate(pdf_paths):
        pdf_reader = PdfReader(pdf_path)
        pdf_writer = PdfWriter()

        # Copy pages from original PDF to writer
        for page_num in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        # Embed the specific part of the Python file as metadata
        pdf_writer.add_metadata({
            '/EncryptedPythonFilePart': content_parts[i].hex(),  # Store as hex
            '/EncryptedAESKey': encrypted_aes_key  # Store AES key in the first file
        })

        # Write the modified PDF to the output folder
        output_pdf_path = os.path.join(output_folder, f"embedded_{os.path.basename(pdf_path)}")
        with open(output_pdf_path, 'wb') as f:
            pdf_writer.write(f)

        print(f"Embedded part {i + 1} of encrypted Python file into {output_pdf_path}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python embed_rsa.py <python_file> <public_key.pem> <pdf_file_1> <pdf_file_2> ... <pdf_file_n>")
        sys.exit(1)

    python_file = sys.argv[1]
    public_key_path = sys.argv[2]
    pdf_files = sys.argv[3:]

    embed_python_in_multiple_pdfs(python_file, pdf_files, public_key_path)
