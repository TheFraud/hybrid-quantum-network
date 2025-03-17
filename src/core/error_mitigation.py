import logging
from typing import Dict, Any
import numpy as np
import asyncio

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.providers.aer import QasmSimulator
# IMPORTANT : Import depuis qiskit_experiments.library pour la mitigation d'erreurs
from qiskit_experiments.library import complete_meas_cal, CompleteMeasFitter

class ErrorMitigationError(Exception):
    """Exception personnalisée pour les erreurs de mitigation."""
    pass

class ErrorMitigation:
    """
    Classe pour la mitigation d'erreurs lors de l'exécution des circuits quantiques.

    Cette classe permet de calibrer le système de mesure et d'appliquer la correction sur
    les résultats obtenus.
    """
    
    def __init__(self, num_qubits: int, shots: int = 1000):
        self.logger = logging.getLogger(__name__)
        self.num_qubits = num_qubits
        self.shots = shots
        self.simulator = QasmSimulator()
        self.meas_fitter: CompleteMeasFitter = None
        self.calibrated = False

    async def calibrate(self) -> None:
        """
        Calibre le système pour la mitigation d'erreurs de mesure.
        
        Il crée et exécute des circuits de calibration, puis initialise le CompleteMeasFitter.
        """
        try:
            self.logger.info("Début de la calibration pour la mitigation d'erreurs")
            
            # Création d'un circuit de calibration pour tous les états possibles
            qr = QuantumRegister(self.num_qubits, "qr")
            cr = ClassicalRegister(self.num_qubits, "cr")
            meas_calibs = complete_meas_cal(qr=qr, circlabel="mcal")
            
            # Exécution des circuits de calibration sur le simulateur
            cal_results = self.simulator.run(meas_calibs, shots=self.shots).result()
            
            # Création d'une liste des états possibles (formats binaires)
            state_labels = [format(i, "0" + str(self.num_qubits) + "b") for i in range(2 ** self.num_qubits)]
            
            # Initialisation du mitigateur de mesure
            self.meas_fitter = CompleteMeasFitter(cal_results, state_labels)
            self.calibrated = True
            self.logger.info("Calibration terminée avec succès")
        except Exception as e:
            self.logger.error(f"Erreur durant la calibration : {str(e)}")
            raise ErrorMitigationError(f"Erreur durant la calibration : {str(e)}")

    async def mitigate(self, circuit: QuantumCircuit) -> Dict[str, Any]:
        """
        Exécute un circuit quantique avec mitigation d'erreurs.
        
        Si la calibration n'a pas encore été effectuée, elle est lancée avant l'exécution.
        
        Args:
            circuit: QuantumCircuit à exécuter et corriger.
            
        Returns:
            Un dictionnaire contenant :
              - 'raw_counts' : résultats bruts du circuit.
              - 'mitigated_counts' : résultats corrigés après mitigation.
        """
        try:
            if not self.calibrated:
                await self.calibrate()
            
            # Exécution du circuit sur le simulateur sans mitigation
            result = self.simulator.run(circuit, shots=self.shots).result()
            raw_counts = result.get_counts(circuit)
            
            # Application de la mitigation d'erreurs sur les résultats
            mitigated_result = self.meas_fitter.filter.apply(result)
            mitigated_counts = mitigated_result.get_counts(circuit)
            
            self.logger.info("Mitigation d'erreurs appliquée avec succès")
            return {
                "raw_counts": raw_counts,
                "mitigated_counts": mitigated_counts
            }
        except Exception as e:
            self.logger.error(f"Erreur durant la mitigation : {str(e)}")
            raise ErrorMitigationError(f"Erreur durant la mitigation : {str(e)}")
