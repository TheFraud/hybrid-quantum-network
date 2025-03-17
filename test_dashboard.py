import pytest
from src.core.hybrid_network import HybridNetwork

def test_dashboard_initialization():
    hn = HybridNetwork(input_size=2, hidden_size=8, output_size=2)
    assert hn is not None

if __name__ == '__main__':
    pytest.main([__file__])
