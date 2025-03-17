import torch
import torch.nn as nn
import numpy as np
from typing import Union, List, Dict, Any

class NeuralNetwork(nn.Module):
    def __init__(self, 
                 input_size: int = 784,
                 hidden_size: int = 256,
                 output_size: int = 10,
                 dropout_rate: float = 0.2):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_size // 2, output_size),
            nn.Sigmoid()
        )
        
        self.criterion = nn.BCELoss()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.to(self.device)

    def _validate_input(self, x: Union[np.ndarray, torch.Tensor, List]) -> torch.Tensor:
        if x is None:
            raise ValueError("Input cannot be None")
        # Conserver le type d'origine pour choisir le format de retour
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
            raise TypeError("Input must be numpy array, list, or torch tensor")
        return x.to(self.device)

    def _validate_target(self, y: Union[np.ndarray, torch.Tensor, List]) -> torch.Tensor:
        if y is None:
            raise ValueError("Target cannot be None")
        if isinstance(y, (list, np.ndarray)):
            y = np.asarray(y, dtype=np.float32)
            if y.ndim == 1:
                y = y.reshape(1, -1)
            elif y.ndim != 2:
                raise ValueError("Target must be 2D")
            y = torch.from_numpy(y)
        elif isinstance(y, torch.Tensor):
            if y.dim() == 1:
                y = y.unsqueeze(0)
            elif y.dim() != 2:
                raise ValueError("Target must be 2D")
        else:
            raise TypeError("Target must be numpy array, list, or torch tensor")
        return y.to(self.device)

    def forward(self, x: Union[np.ndarray, torch.Tensor, List]) -> Union[torch.Tensor, np.ndarray]:
        # Conserver le type d'origine de l'entrée
        orig_type = type(x)
        x_tensor = self._validate_input(x)
        output = self.network(x_tensor)
        # Si l'utilisateur a passé une liste ou un numpy array, on retourne un numpy array.
        if orig_type in [list, np.ndarray]:
            return output.cpu().detach().numpy()
        return output

    def backward(self, x: Union[np.ndarray, List, torch.Tensor],
                 y: Union[np.ndarray, List, torch.Tensor],
                 learning_rate: float = 0.01) -> float:
        self.train(True)
        x_tensor = self._validate_input(x)
        y_tensor = self._validate_target(y)
        optimizer = torch.optim.Adam(self.parameters(), lr=learning_rate)
        optimizer.zero_grad()
        output = self(x_tensor)
        loss = self.criterion(output, y_tensor)
        loss.backward()
        optimizer.step()
        return loss.item()

    def train_model(self, x: Union[np.ndarray, List, torch.Tensor],
                    y: Union[np.ndarray, List, torch.Tensor],
                    epochs: int = 1,
                    learning_rate: float = 0.01) -> float:
        self.train(True)
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

    def predict(self, x: Union[np.ndarray, List, torch.Tensor]) -> np.ndarray:
        self.eval()
        with torch.no_grad():
            output = self(x)
            if isinstance(output, torch.Tensor):
                return output.cpu().detach().numpy()
            return output

    def train(self, *args, **kwargs) -> Union['NeuralNetwork', float]:
        # Sans argument ou avec un booléen, on active/désactive le mode entraînement.
        if not args and not kwargs:
            return super().train()
        if len(args) == 1 and isinstance(args[0], bool):
            return super().train(args[0])
        # Avec des données (x, y)
        if len(args) >= 2:
            x, y = args[0], args[1]
            epochs = kwargs.get('epochs', 1)
            learning_rate = kwargs.get('learning_rate', 0.01)
            return self.train_model(x, y, epochs=epochs, learning_rate=learning_rate)
        if 'x' in kwargs and 'y' in kwargs:
            x = kwargs.pop('x')
            y = kwargs.pop('y')
            epochs = kwargs.get('epochs', 1)
            learning_rate = kwargs.get('learning_rate', 0.01)
            return self.train_model(x, y, epochs=epochs, learning_rate=learning_rate)
        return super().train()

    def eval(self) -> 'NeuralNetwork':
        return super().train(False)

    def get_state(self) -> Dict[str, Any]:
        return {
            'input_size': self.input_size,
            'hidden_size': self.hidden_size,
            'output_size': self.output_size,
            'state_dict': self.state_dict()
        }

    def load_state(self, state: Dict[str, Any]) -> None:
        self.load_state_dict(state['state_dict'])
