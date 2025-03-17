import pytest
import numpy as np
from src.core.hybrid_network import HybridNetwork
from src.core.quantum_processor import QuantumProcessor

@pytest.fixture(scope="class")
def quantum_processor(request):
    """Fixture pour le processeur quantique"""
    request.cls.quantum_processor = QuantumProcessor(n_qubits=2)
    return request.cls.quantum_processor

@pytest.mark.usefixtures("quantum_processor")
class TestHybridNetwork:
    def test_initialization(self):
        """Test l'initialisation du réseau hybride"""
        hybrid_net = HybridNetwork(
            input_size=2,
            hidden_size=8,
            output_size=2,
            quantum_processor=self.quantum_processor
        )
        
        assert hybrid_net.input_size == 2
        assert hybrid_net.hidden_size == 8
        assert hybrid_net.output_size == 2
        assert hasattr(hybrid_net, 'quantum_processor')
        assert isinstance(hybrid_net.quantum_processor, QuantumProcessor)

    def test_process(self):
        """Test le traitement des données"""
        hybrid_net = HybridNetwork(
            input_size=2,
            hidden_size=8,
            output_size=2,
            quantum_processor=self.quantum_processor
        )
        
        test_inputs = [
            np.array([0.5, 0.5]),
            np.array([[0.1, 0.9]]),
            np.array([[0.3, 0.7], [0.2, 0.8]])
        ]
        
        for input_data in test_inputs:
            result = hybrid_net.process(input_data)
            assert result is not None
            assert isinstance(result, np.ndarray)
            
            if input_data.ndim == 1:
                assert result.shape == (1, 2)
            else:
                assert result.shape == (input_data.shape[0], 2)

    def test_training(self):
        """Test l'entraînement du réseau"""
        hybrid_net = HybridNetwork(
            input_size=2,
            hidden_size=8,
            output_size=2,
            quantum_processor=self.quantum_processor
        )
        
        X_train = np.random.rand(10, 2)
        y_train = np.random.randint(0, 2, size=(10, 2))
        
        initial_loss = hybrid_net.train(X_train, y_train, epochs=1)
        final_loss = hybrid_net.train(X_train, y_train, epochs=5)
        
        assert isinstance(initial_loss, float)
        assert isinstance(final_loss, float)
        assert final_loss <= initial_loss

    def test_prediction(self):
        """Test les prédictions"""
        hybrid_net = HybridNetwork(
            input_size=2,
            hidden_size=8,
            output_size=2,
            quantum_processor=self.quantum_processor
        )
        
        X_test = np.random.rand(5, 2)
        predictions = hybrid_net.predict(X_test)
        
        assert predictions.shape == (5, 2)
        assert np.all((predictions >= 0) & (predictions <= 1))

    def test_error_handling(self):
        """Test la gestion des erreurs"""
        hybrid_net = HybridNetwork(
            input_size=2,
            hidden_size=8,
            output_size=2,
            quantum_processor=self.quantum_processor
        )
        
        invalid_inputs = [
            None,
            "invalid",
            np.array([1, 2, 3]),
            np.zeros((3, 2, 1))
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises((ValueError, TypeError)):
                hybrid_net.process(invalid_input)
