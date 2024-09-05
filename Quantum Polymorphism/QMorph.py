from qiskit import QuantumCircuit
from qiskit.execute_function import execute
from qiskit_aer import AerSimulator


def genQRNG(num_bits):

    qc = QuantumCircuit(num_bits, num_bits)
    for i in range(num_bits):
        qc.h(i)
    qc.measure(range(num_bits), range(num_bits))
    simulator = AerSimulator()
    job = execute(qc, simulator, shots=1)
    result = job.result()
    counts = result.get_counts()
    return list(counts.keys())[0]


def mutation(program):

    quantum_bits = genQRNG(8)
    mutation_factor = int(quantum_bits, 2)

    shift_amount = mutation_factor % len(program)
    mutated_code = program[shift_amount:] + program[:shift_amount]

    return mutated_code


# Work in Progress