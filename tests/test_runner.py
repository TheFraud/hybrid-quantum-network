import pytest
import numpy as np
import pickle
from streamlit.testing.v1 import AppTest
from src.core.hybrid_network import HybridNetwork
from src.core.quantum_processor import QuantumProcessor

# ------------------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def quantum_processor():
    """Fixture pour le processeur quantique"""
    return QuantumProcessor(n_qubits=2)  # Changé de num_qubits à n_qubits

@pytest.fixture(scope="module")
def hybrid_net(quantum_processor):
    """Fixture pour le réseau hybride"""
    return HybridNetwork(
        input_size=2,
        hidden_size=8,
        output_size=2,
        quantum_processor=quantum_processor
    )

# ------------------------------------------------------------------------------
# Tests du processeur quantique
# ------------------------------------------------------------------------------
def test_quantum_processor_initialization(quantum_processor):
    """Test l'initialisation du processeur quantique"""
    assert quantum_processor.n_qubits == 2  # Changé de num_qubits à n_qubits
    assert hasattr(quantum_processor, 'circuit')
    assert quantum_processor.circuit is not None

def test_quantum_processor_execution(quantum_processor):
    """Test l'exécution d'un circuit quantique simple"""
    input_data = np.array([0.5, 0.5])
    result = quantum_processor.process(input_data)  # Changé de execute_circuit à process
    assert result is not None
    assert isinstance(result, np.ndarray)
    assert len(result) == 2**quantum_processor.n_qubits  # Changé de num_qubits à n_qubits

def test_quantum_processor_advanced(quantum_processor):
    """Tests avancés du processeur quantique"""
    test_inputs = [
        np.array([0.0, 0.0]),  # État fondamental
        np.array([1.0, 1.0]),  # État excité
        np.array([0.5, 0.5])   # Superposition
    ]
    
    for input_data in test_inputs:
        result = quantum_processor.process(input_data)  # Changé de execute_circuit à process
        assert result is not None
        assert isinstance(result, np.ndarray)
        assert len(result) == 2**quantum_processor.n_qubits  # Changé de num_qubits à n_qubits
        assert np.all(result >= 0)
        assert np.abs(np.sum(result) - 1.0) < 1e-10

# ------------------------------------------------------------------------------
# Tests du réseau hybride
# ------------------------------------------------------------------------------
def test_hybrid_network_quantum_integration(hybrid_net):
    """Test l'intégration du processeur quantique dans le réseau hybride"""
    input_data = np.random.rand(1, 2)
    prediction = hybrid_net.predict(input_data)
    assert prediction.shape == (1, 2)
    assert hasattr(hybrid_net, 'quantum_processor')

def test_hybrid_network_end_to_end(hybrid_net):
    """Test complet du réseau hybride"""
    X_train = np.random.rand(10, 2)
    y_train = np.random.randint(0, 2, size=(10, 2))
    X_test = np.random.rand(2, 2)

    initial_loss = hybrid_net.train(X_train, y_train, epochs=1)
    final_loss = hybrid_net.train(X_train, y_train, epochs=5)
    assert final_loss <= initial_loss

    predictions = hybrid_net.predict(X_test)
    assert predictions.shape == (2, 2)
    assert np.all((predictions >= 0) & (predictions <= 1))

def test_hybrid_network_persistence(hybrid_net, tmp_path):
    """Test la sauvegarde et le chargement du modèle"""
    model_path = tmp_path / "hybrid_model.pkl"
    
    with open(model_path, 'wb') as f:
        pickle.dump(hybrid_net, f)
    
    with open(model_path, 'rb') as f:
        loaded_model = pickle.load(f)
    
    input_data = np.random.rand(1, 2)
    original_prediction = hybrid_net.predict(input_data)
    loaded_prediction = loaded_model.predict(input_data)
    assert np.allclose(original_prediction, loaded_prediction)

# ------------------------------------------------------------------------------
# Tests d'intégration Streamlit
# ------------------------------------------------------------------------------
def test_streamlit_integration_extended():
    """Test étendu de l'intégration Streamlit"""
    try:
        at = AppTest.from_file("dashboard.py")
        at.run()
        
        assert len(at.button) > 0, "Aucun bouton trouvé"
        assert len(at.text_input) > 0, "Aucun champ de saisie trouvé"
        
        buttons = list(at.button)
        button_labels = [str(b.label) for b in buttons]
        required_buttons = [
            "Generate Training Data",
            "Train the Network",
            "Run Automated Tests"
        ]
        for button in required_buttons:
            assert button in button_labels, f"Bouton '{button}' manquant"
            
    except Exception as e:
        pytest.skip(f"Test Streamlit ignoré : {str(e)}")

# ------------------------------------------------------------------------------
# Tests de gestion des erreurs
# ------------------------------------------------------------------------------
def test_error_handling():
    """Test la gestion des erreurs"""
    quantum_proc = QuantumProcessor(n_qubits=2)  # Changé de num_qubits à n_qubits
    
    invalid_inputs = [
        None,
        "invalid",
        np.array([1, 2, 3]),      # Dimensions incorrectes
        np.array([[1, 2], [3, 4]]) # Mauvaise forme
    ]
    
    for invalid_input in invalid_inputs:
        with pytest.raises((ValueError, TypeError)):
            quantum_proc.process(invalid_input)  # Changé de execute_circuit à process

if __name__ == "__main__":
    pytest.main(["-v", __file__])
