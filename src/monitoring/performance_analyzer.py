import psutil
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

class PerformanceAnalyzer:
    """
    Analyse et suivi des performances système.

    Collecte régulièrement des métriques telles que l'utilisation du CPU, de la mémoire,
    du disque et du réseau.
    """
    def __init__(self, interval: int = 5):
        """
        Args:
            interval (int): Intervalle en secondes entre deux collectes.
        """
        self.logger = logging.getLogger(__name__)
        self.interval = interval
        self.metrics: Dict[str, Any] = {}
        self.running = False

    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collecte les métriques du système.

        Returns:
            dict: Dictionnaire des métriques.
        """
        metrics = {}
        try:
            metrics["timestamp"] = datetime.utcnow().isoformat()
            metrics["cpu_percent"] = psutil.cpu_percent(interval=1)
            metrics["memory"] = psutil.virtual_memory()._asdict()
            metrics["disk"] = psutil.disk_usage("/")._asdict()
            metrics["net_io"] = psutil.net_io_counters()._asdict()
            self.logger.debug(f"Métriques collectées : {metrics}")
        except Exception as e:
            self.logger.error(f"Erreur de collecte de métriques : {str(e)}")
        return metrics

    async def start(self):
        """Démarre la collecte continue des métriques."""
        self.running = True
        while self.running:
            self.metrics = self.collect_metrics()
            self.logger.info(f"Métriques : {self.metrics}")
            await asyncio.sleep(self.interval)

    async def stop(self):
        """Arrête la collecte continue des métriques."""
        self.running = False

