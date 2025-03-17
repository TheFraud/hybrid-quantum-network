import pytest
import numpy as np
from src.core.hybrid_network import HybridNetwork

@pytest.fixture
def hybrid_net():
    return HybridNetwork(input_size=2, hidden_size=8, output_size=2)

def test_hybrid_network_initialization(hybrid_net):
    assert hybrid_net.input_size == 2
    assert hybrid_net.neural_network.hidden_size == 8
    assert hybrid_net.neural_network.output_size == 2

def test_hybrid_network_prediction(hybrid_net):
    input_data = np.random.rand(1, 2)
    prediction = hybrid_net.predict(input_data)
    assert prediction.shape == (1, 2)

if __name__ == "__main__":
    pytest.main([__file__])
