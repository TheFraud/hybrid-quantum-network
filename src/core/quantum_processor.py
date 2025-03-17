from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
import numpy as np
from typing import Dict, Any, Union, List

class QuantumProcessor:
    def __init__(self, n_qubits: int = 2):
        self.n_qubits = n_qubits
        self.qr = QuantumRegister(n_qubits)
        self.cr = ClassicalRegister(n_qubits)
        self._initialize_circuit()
        self.backend = AerSimulator(seed_simulator=42)

    def _initialize_circuit(self):
        self.circuit = QuantumCircuit(self.qr, self.cr)
        for i in range(self.n_qubits):
            self.circuit.h(i)

    def _validate_input(self, input_data: Union[np.ndarray, List]) -> np.ndarray:
        if input_data is None:
            raise ValueError("Input cannot be None")
        if not isinstance(input_data, (np.ndarray, list)):
            raise TypeError(f"Input must be numpy array or list, got {type(input_data)}")
        try:
            input_data = np.asarray(input_data, dtype=np.float32)
        except Exception:
            raise TypeError("Could not convert input to numpy array")
        if input_data.ndim == 1:
            if input_data.shape[0] != self.n_qubits:
                raise ValueError(f"Input size must match number of qubits: {self.n_qubits}")
            input_data = input_data.reshape(1, -1)
        elif input_data.ndim == 2:
            if input_data.shape[1] != self.n_qubits:
                raise ValueError(f"Input must be of shape (batch_size, {self.n_qubits})")
            # For ce processeur, nous attendons un seul échantillon.
            if input_data.shape[0] != 1:
                raise ValueError("QuantumProcessor expects a single sample as input.")
        else:
            raise ValueError(f"Input must be 1D or 2D, got {input_data.ndim}D")
        return input_data

    def process(self, input_data: Union[np.ndarray, List]) -> np.ndarray:
        """
        Exécute le circuit quantique et retourne le vecteur d'état (probabilités)
        normalisé sous forme de numpy.ndarray.
        """
        validated_input = self._validate_input(input_data)
        self._initialize_circuit()
        for i in range(self.n_qubits):
            self.circuit.ry(float(validated_input[0, i]) * np.pi, i)
        self.circuit.measure_all()
        job = self.backend.run(self.circuit, shots=1000)
        result = job.result()
        counts = result.get_counts()
        total_shots = sum(counts.values())
        state_vector = np.zeros(2 ** self.n_qubits, dtype=np.float32)
        for state, count in counts.items():
            state_clean = state.replace(" ", "")
            idx = int(state_clean[-self.n_qubits:], 2)
            state_vector[idx] = count / total_shots
        state_vector = state_vector / np.sum(state_vector)
        return state_vector

    def reset(self):
        self._initialize_circuit()

    def get_circuit_depth(self) -> int:
        return self.circuit.depth() if self.circuit else 0

    def get_circuit_size(self) -> Dict[str, int]:
        return {
            'n_qubits': self.n_qubits,
            'n_classical_bits': len(self.cr),
            'depth': self.get_circuit_depth()
        }
