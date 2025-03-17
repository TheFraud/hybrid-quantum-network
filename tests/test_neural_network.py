import unittest
import numpy as np
from src.core.neural_network import NeuralNetwork

class TestNeuralNetwork(unittest.TestCase):
    def setUp(self):
        self.nn = NeuralNetwork(input_size=3, hidden_size=4, output_size=2)

    def test_forward_pass(self):
        input_data = [[0.1, 0.2, 0.3]]
        output = self.nn.forward(input_data)
        self.assertEqual(output.shape, (1, 2))
        self.assertTrue(np.all((output >= 0) & (output <= 1)))

    def test_backward_pass(self):
        input_data = [[0.1, 0.2, 0.3]]
        target = [[1, 0]]
        self.nn.forward(input_data)
        loss = self.nn.backward(input_data, target, learning_rate=0.01)
        self.assertIsNotNone(loss)
        self.assertIsInstance(loss, float)
        self.assertTrue(loss >= 0)

    def test_training(self):
        training_data = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        targets = [[1, 0], [0, 1]]
        initial_loss = self.nn.train(training_data, targets, epochs=1, learning_rate=0.01)
        self.assertIsInstance(initial_loss, float)
        self.assertTrue(initial_loss >= 0)

    def test_prediction(self):
        input_data = [0.1, 0.2, 0.3]
        prediction = self.nn.predict([input_data])
        self.assertEqual(prediction.shape, (1, 2))
        self.assertTrue(np.all((prediction >= 0) & (prediction <= 1)))

if __name__ == '__main__':
    unittest.main()
