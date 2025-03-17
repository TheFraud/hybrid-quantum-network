import pytest
import sys
import os
import asyncio
from src.core.quantum_processor import QuantumProcessor
from src.core.hybrid_network import HybridNetwork

# Add project root to PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def quantum_processor():
    """Fixture for quantum processor"""
    return QuantumProcessor(num_qubits=2)  # Utilise num_qubits au lieu de n_qubits

@pytest.fixture(scope="session")
def hybrid_network(quantum_processor):
    """Fixture for hybrid network with quantum processor"""
    return HybridNetwork(
        input_size=2, 
        hidden_size=8, 
        output_size=2,
        quantum_processor=quantum_processor
    )

