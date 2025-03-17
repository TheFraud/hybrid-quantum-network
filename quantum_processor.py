# src/core/quantum_processor.py
from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit.compiler import execute
import numpy as np

class QuantumProcessor:
    def __init__(self):
        self.backend = Aer.get_backend('qasm_simulator')

    def prepare_state(self, input_data):
        num_qubits = len(input_data)
        qc = QuantumCircuit(num_qubits, num_qubits)
        
        for i, value in enumerate(input_data):
            qc.ry(np.pi * value, i)
        
        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)
        
        qc.measure_all()
        return qc

    def process(self, input_data):
        try:
            qc = self.prepare_state(input_data)
            job = execute(qc, self.backend, shots=1000)
            result = job.result()
            counts = result.get_counts(qc)
            return self.postprocess_counts(counts, len(input_data))
        except Exception as e:
            print(f"Error in quantum processing: {str(e)}")
            return [0] * (2**len(input_data))  # Return default values in case of error

    def postprocess_counts(self, counts, num_qubits):
        total_shots = sum(counts.values())
        probabilities = [
            counts.get(format(i, f'0{num_qubits}b'), 0) / total_shots 
            for i in range(2**num_qubits)
        ]
        return probabilities
