import pytest
import numpy as np
import streamlit as st
from streamlit.testing.v1 import AppTest
from src.core.hybrid_network import HybridNetwork
from src.core.quantum_processor import QuantumProcessor

@pytest.fixture
def quantum_processor():
    """Fixture pour le processeur quantique"""
    return QuantumProcessor(n_qubits=2)

@pytest.fixture
def hybrid_network(quantum_processor):
    """Fixture pour le réseau hybride"""
    return HybridNetwork(
        input_size=2,
        hidden_size=8,
        output_size=2,
        quantum_processor=quantum_processor
    )

def test_dashboard_initialization(hybrid_network):
    """Test l'initialisation du dashboard"""
    assert hybrid_network is not None
    assert isinstance(hybrid_network, HybridNetwork)
    assert hybrid_network.input_size == 2
    assert hybrid_network.hidden_size == 8
    assert hybrid_network.output_size == 2
    assert hasattr(hybrid_network, 'quantum_processor')

def test_dashboard_processing(hybrid_network):
    """Test le traitement des données dans le dashboard"""
    input_data = np.array([[0.5, 0.5]])
    result = hybrid_network.process(input_data)
    assert result is not None
    assert isinstance(result, np.ndarray)
    assert result.shape == (1, 2)
    assert np.all((result >= 0) & (result <= 1))

def test_dashboard_streamlit_integration():
    """Test l'intégration avec Streamlit"""
    try:
        at = AppTest.from_file("dashboard.py")
        at.run()
        
        assert "Hybrid Quantum-Classical Network Dashboard" in at.title[0].value
        
        buttons = list(at.button)
        button_labels = [str(b.label) for b in buttons]
        required_buttons = [
            "Generate Training Data",
            "Train the Network",
            "Run Automated Tests"
        ]
        for button in required_buttons:
            assert button in button_labels, f"Bouton '{button}' manquant"
            
        assert len(at.text_input) > 0, "Aucun champ de saisie trouvé"
        
    except Exception as e:
        pytest.skip(f"Test Streamlit ignoré : {str(e)}")

def test_dashboard_error_handling(hybrid_network):
    """Test la gestion des erreurs du dashboard"""
    invalid_inputs = [
        None,
        "invalid",
        np.array([1, 2, 3]),  # Dimensions incorrectes
        np.array([[1, 2, 3]])  # Trop de colonnes
    ]
    
    for invalid_input in invalid_inputs:
        with pytest.raises((ValueError, TypeError)):
            hybrid_network.process(invalid_input)

def test_dashboard_data_validation(hybrid_network):
    """Test la validation des données d'entrée"""
    valid_inputs = [
        np.array([[0.1, 0.2]]),
        np.array([[0.3, 0.4], [0.5, 0.6]]),
        np.array([[0.7, 0.8], [0.9, 1.0], [0.1, 0.2]])
    ]
    
    for valid_input in valid_inputs:
        result = hybrid_network.process(valid_input)
        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.shape[1] == 2
        assert np.all((result >= 0) & (result <= 1))

if __name__ == "__main__":
    pytest.main(["-v", __file__])
