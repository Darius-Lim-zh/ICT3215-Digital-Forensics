from Crypto.Cipher import AES
import logging

logging.basicConfig(level=logging.INFO)


def load_key_from_file(filename):
    with open(filename, 'rb') as file:
        return file.read()


def load_encrypted_program(filename):
    with open(filename, 'rb') as file:
        return file.read()


def decrypt_data(encrypted_data, key):
    try:
        #Salt is in the first 16 bytes so we ignore it
        nonce = encrypted_data[:16]
        tag = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]

        logging.info(f"Nonce: {nonce}")
        logging.info(f"Tag: {tag}")
        logging.info(f"Ciphertext Length: {len(ciphertext)}")

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        logging.info(f"Plaintext: {plaintext}")
        return plaintext
    except ValueError as e:
        logging.error(f"Decryption failed: {e}")
        raise
    except Exception as e:
        logging.error(f"An error occurred during decryption: {e}")
        raise


def save_decrypted_program(decrypted_program, filename):
    with open(filename, 'wb') as file:
        file.write(decrypted_program)


def main():
    try:
        key_file = 'qrng_aes256_key.bin'
        encrypted_program_file = 'encrypted_program.bin'
        decrypted_program_file = 'decrypted_program.py'

        quantum_key = load_key_from_file(key_file)
        logging.info(f"Quantum key loaded: {quantum_key}")

        encrypted_program = load_encrypted_program(encrypted_program_file)
        logging.info(f"Encrypted program loaded: {encrypted_program}")

        salt = encrypted_program[:16]
        logging.info(f"Extracted Salt: {salt}")

        aes_key = quantum_key
        logging.info(f"AES key: {aes_key}")

        decrypted_program = decrypt_data(encrypted_program[16:], aes_key)

        save_decrypted_program(decrypted_program, decrypted_program_file)
        logging.info("Decrypted program saved successfully.")
    except Exception as e:
        logging.error(f"An error occurred during the decryption process: {e}")


if __name__ == "__main__":
    main()
