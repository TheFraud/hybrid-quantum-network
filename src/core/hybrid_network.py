import torch
import torch.nn as nn
import numpy as np
from typing import Union, List, Optional, Dict, Any
from .neural_network import NeuralNetwork
from .quantum_processor import QuantumProcessor

class HybridNetwork(nn.Module):
    def __init__(self, 
                 input_size: int = 2,
                 hidden_size: int = 8,
                 output_size: int = 2,
                 n_qubits: int = 2,
                 quantum_depth: int = 3,
                 fusion_mode: str = "concat",
                 quantum_weight: float = 0.5,
                 quantum_processor: Optional[QuantumProcessor] = None):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.n_qubits = n_qubits
        self.quantum_depth = quantum_depth
        self.fusion_mode = fusion_mode
        self.quantum_weight = quantum_weight
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.quantum_processor = quantum_processor or QuantumProcessor(n_qubits=n_qubits)
        self.classical_network = NeuralNetwork(
            input_size=input_size,
            hidden_size=hidden_size,
            output_size=hidden_size  # produit un tenseur de dimension hidden_size
        )
        
        fusion_input_dim = hidden_size + (2 ** n_qubits) if fusion_mode == "concat" else hidden_size
        self.fusion_layer = nn.Linear(fusion_input_dim, output_size)
        self.output_layer = nn.Linear(output_size, output_size)
        self.activation = nn.Sigmoid()
        self.criterion = nn.BCELoss()
        self.to(self.device)

    def _validate_input(self, x: Union[np.ndarray, torch.Tensor, List]) -> torch.Tensor:
        if x is None:
            raise ValueError("Input cannot be None")
        if isinstance(x, (list, np.ndarray)):
            x = np.asarray(x, dtype=np.float32)
            if x.ndim == 1:
                if x.shape[0] != self.input_size:
                    raise ValueError(f"Expected input dimension {self.input_size}, got {x.shape[0]}")
                x = x.reshape(1, -1)
            elif x.ndim == 2:
                if x.shape[1] != self.input_size:
                    raise ValueError(f"Input must be of shape (batch_size, {self.input_size})")
            else:
                raise ValueError("Input must be 1D or 2D")
            x = torch.from_numpy(x)
        elif isinstance(x, torch.Tensor):
            if x.dim() == 1:
                if x.shape[0] != self.input_size:
                    raise ValueError(f"Expected input dimension {self.input_size}, got {x.shape[0]}")
                x = x.unsqueeze(0)
            elif x.dim() == 2:
                if x.shape[1] != self.input_size:
                    raise ValueError(f"Input must be of shape (batch_size, {self.input_size})")
            else:
                raise ValueError("Input tensor must be 1D or 2D")
        else:
            raise TypeError("Input must be a numpy array, list, or torch tensor")
        return x.to(self.device)

    def _validate_target(self, y: Union[np.ndarray, torch.Tensor, List]) -> torch.Tensor:
        if y is None:
            raise ValueError("Target cannot be None")
        if isinstance(y, (list, np.ndarray)):
            y = np.asarray(y, dtype=np.float32)
            if y.ndim == 1:
                if y.shape[0] != self.output_size:
                    raise ValueError(f"Expected target dimension {self.output_size}, got {y.shape[0]}")
                y = y.reshape(1, -1)
            elif y.ndim == 2:
                if y.shape[1] != self.output_size:
                    raise ValueError(f"Target must be of shape (batch_size, {self.output_size})")
            else:
                raise ValueError("Target must be 1D or 2D")
            y = torch.from_numpy(y)
        elif isinstance(y, torch.Tensor):
            if y.dim() == 1:
                if y.shape[0] != self.output_size:
                    raise ValueError(f"Expected target dimension {self.output_size}, got {y.shape[0]}")
                y = y.unsqueeze(0)
            elif y.dim() == 2:
                if y.shape[1] != self.output_size:
                    raise ValueError(f"Target must be of shape (batch_size, {self.output_size})")
            else:
                raise ValueError("Target tensor must be 1D or 2D")
        else:
            raise TypeError("Target must be a numpy array, list, or torch tensor")
        return y.to(self.device)

    def forward(self, x: Union[np.ndarray, torch.Tensor, List]) -> Union[torch.Tensor, np.ndarray]:
        try:
            x_tensor = self._validate_input(x)
            # Passage par le réseau classique.
            classical_output = self.classical_network(x_tensor)
            if isinstance(classical_output, np.ndarray):
                classical_output = torch.from_numpy(classical_output).float().to(self.device)
            # Passage par le processeur quantique (on utilise le premier échantillon).
            quantum_input = x_tensor[0:1].cpu().detach().numpy()
            quantum_state = self.quantum_processor.process(quantum_input)
            quantum_tensor = torch.tensor(quantum_state, dtype=torch.float32).to(self.device)
            # Répéter pour chaque échantillon du batch.
            batch_size = x_tensor.shape[0]
            quantum_tensor = quantum_tensor.unsqueeze(0).expand(batch_size, -1)
            # Fusion selon le mode choisi.
            if self.fusion_mode == "concat":
                fused = torch.cat([classical_output, quantum_tensor], dim=1)
            else:
                fused = classical_output + self.quantum_weight * quantum_tensor
            out = self.fusion_layer(fused)
            out = self.output_layer(out)
            out = self.activation(out)
            if not self.training:
                return out.cpu().detach().numpy()
            return out
        except Exception as e:
            if isinstance(e, (ValueError, TypeError)):
                raise
            raise RuntimeError(f"Forward pass error: {str(e)}")

    def train_model(self, x: Union[np.ndarray, List], y: Union[np.ndarray, List],
                   epochs: int = 1, learning_rate: float = 0.001) -> float:
        if x is None or y is None:
            raise ValueError("Training data and targets cannot be None")
        super().train(True)
        x_tensor = self._validate_input(x)
        y_tensor = self._validate_target(y)
        optimizer = torch.optim.Adam(self.parameters(), lr=learning_rate)
        total_loss = 0.0
        for _ in range(epochs):
            optimizer.zero_grad()
            outputs = self(x_tensor)
            loss = self.criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        return total_loss / epochs

    def predict(self, x: Union[np.ndarray, List]) -> np.ndarray:
        self.eval()
        with torch.no_grad():
            return self(x)

    def process(self, x: Union[np.ndarray, List]) -> np.ndarray:
        return self.predict(x)

    def train(self, x: Optional[Union[np.ndarray, List]] = None,
             y: Optional[Union[np.ndarray, List]] = None,
             **kwargs) -> Union['HybridNetwork', float]:
        if x is None and y is None:
            return super().train()
        if x is not None and y is not None:
            epochs = kwargs.get('epochs', 1)
            learning_rate = kwargs.get('learning_rate', 0.001)
            return self.train_model(x, y, epochs=epochs, learning_rate=learning_rate)
        raise ValueError("Both x and y must be provided for training")

    def eval(self) -> 'HybridNetwork':
        return super().train(False)

    def save_state(self, filepath: str) -> None:
        try:
            torch.save({
                'model_state': self.state_dict(),
                'config': self.get_config()
            }, filepath)
        except Exception as e:
            raise RuntimeError(f"Save state error: {str(e)}")

    def load_state(self, filepath: str) -> None:
        try:
            checkpoint = torch.load(filepath)
            self.load_state_dict(checkpoint['model_state'])
            config = checkpoint['config']
            for key, value in config.items():
                setattr(self, key, value)
        except Exception as e:
            raise RuntimeError(f"Load state error: {str(e)}")

    def get_config(self) -> Dict[str, Any]:
        return {
            'input_size': self.input_size,
            'hidden_size': self.hidden_size,
            'output_size': self.output_size,
            'n_qubits': self.n_qubits,
            'quantum_depth': self.quantum_depth,
            'fusion_mode': self.fusion_mode,
            'quantum_weight': self.quantum_weight
        }
