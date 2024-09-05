from qiskit import QuantumCircuit
from qiskit.execute_function import execute
from qiskit_aer import AerSimulator
from Crypto.Cipher import AES


def generate_qrng_bits(num_bits=256, batch_size=16):
    simulator = AerSimulator()
    random_bits = ""

    # Qiskit has 29 qubit limitation, so we need to run in batches
    for _ in range(num_bits // batch_size):
        qc = QuantumCircuit(batch_size, batch_size)

        for qubit in range(batch_size):
            qc.h(qubit)

        qc.measure(range(batch_size), range(batch_size))

        result = execute(qc, simulator, shots=1).result()
        counts = result.get_counts()

        measured_bits = list(counts.keys())[0]
        random_bits += measured_bits

    return random_bits[:num_bits]


def format_key_as_bytes(bitstring):
    bitstring = bitstring[:256]
    return int(bitstring, 2).to_bytes(32, byteorder='big')


# AES-GCM does not require salt, but we can use it to add more confusion
def format_salt_as_bytes(bitstring):
    bitstring = bitstring[:128]
    return int(bitstring, 2).to_bytes(16, byteorder='big')


def load_program_to_encrypt(filename):
    with open(filename, 'rb') as file:
        return file.read()


def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_GCM)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)
    print(f"Generated Nonce: {nonce}")
    print(f"Tag: {tag}")
    print(f"Ciphertext Length: {len(ciphertext)}")
    return nonce + tag + ciphertext


def save_encrypted_program(encrypted_data, filename):
    with open(filename, 'wb') as file:
        file.write(encrypted_data)


def save_key_to_file(key, filename='qrng_aes256_key.bin'):
    with open(filename, 'wb') as file:
        file.write(key)


# Main function to combine QRNG with AES encryption and save the key
def main():
    try:
        # Generate 256 bits of quantum randomness
        quantum_bits = generate_qrng_bits(384, batch_size=16)
        print(f"Generated Quantum Random Bits: {quantum_bits}")

        aes_key = format_key_as_bytes(quantum_bits[:256])
        print(f"AES-256 Key (hex): {aes_key.hex()}")

        key_file = 'qrng_aes256_key.bin'
        save_key_to_file(aes_key, key_file)
        print(f"Quantum AES-256 key saved to '{key_file}'.")

        salt = format_salt_as_bytes(quantum_bits[256:384])
        print(f"Generated Salt (from QRNG): {salt}")

        program_file = 'test.py'
        program_data = load_program_to_encrypt(program_file)

        encrypted_program = encrypt_data(program_data, aes_key)

        encrypted_program = salt + encrypted_program

        encrypted_program_file = 'encrypted_program.bin'
        save_encrypted_program(encrypted_program, encrypted_program_file)
        print(f"Encrypted program saved to '{encrypted_program_file}'.")

    except Exception as e:
        print(f"An error occurred during the encryption process: {e}")


if __name__ == "__main__":
    main()
