# src/data/collector.py

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
import aiohttp
from ..memory.memory_manager import MemoryManager

class CollectorError(Exception):
    """Custom exception for Collector errors"""
    pass

class DataCollector:
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialise le collecteur de données.

        Args:
            memory_manager: Gestionnaire de mémoire pour le stockage des données.
        """
        self.logger = logging.getLogger(__name__)
        self.memory_manager = memory_manager
        self.running = False
        self.config = self._load_config()
        self._initialize_components()
        self.session = None

    def _load_config(self) -> Dict[str, Any]:
        """Charge la configuration pour le collecteur"""
        try:
            config = {
                "sources": {
                    "internet_archive": {
                        "enabled": True,
                        "priority": 1,
                        "rate_limit": 100
                    },
                    "github": {
                        "enabled": True,
                        "priority": 2,
                        "rate_limit": 5000
                    }
                },
                "batch_size": 32,
                "update_interval": 3600,
                "search_queries": [
                    "quantum computing",
                    "neural networks",
                    "hybrid AI"
                ]
            }
            return config
        except Exception as e:
            self.logger.error(f"Erreur chargement config: {str(e)}")
            raise CollectorError(f"Configuration invalide: {str(e)}")

    def _initialize_components(self) -> None:
        """Initialise les composants du collecteur"""
        try:
            self.sources = self.config.get("sources", {})
            self.batch_size = self.config.get("batch_size", 32)
            self.update_interval = self.config.get("update_interval", 3600)
            self.search_queries = self.config.get("search_queries", [])
        except Exception as e:
            self.logger.error(f"Erreur initialisation composants: {str(e)}")
            raise CollectorError(f"Erreur initialisation: {str(e)}")

    async def collect_continuously(self) -> Dict[str, Any]:
        """Collecte continue des données depuis les sources configurées"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            collected_data = {
                'text': '',
                'metadata': {},
                'timestamp': time.time()
            }
            
            # Collecte depuis les sources activées
            for source_name, config in self.sources.items():
                if config.get("enabled", False):
                    try:
                        data = await self._collect_from_source(source_name, config)
                        if data:
                            collected_data['text'] += f"\n{data.get('text', '')}"
                            collected_data['metadata'].update(data.get('metadata', {}))
                    except Exception as e:
                        self.logger.error(f"Erreur collecte depuis {source_name}: {str(e)}")
                        
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Erreur dans la collecte continue: {str(e)}")
            return {}

    async def _collect_from_source(self, source_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Collecte les données depuis une source spécifique"""
        if source_name == "internet_archive":
            return await self._collect_from_archive(config)
        elif source_name == "github":
            return await self._collect_from_github(config)
        return {}

    async def _collect_from_archive(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Collecte les données depuis Internet Archive"""
        try:
            async with self.session.get(
                "https://archive.org/advancedsearch.php",
                params={
                    "q": " OR ".join(self.search_queries),
                    "fl[]": "identifier,title,description",
                    "rows": config.get("rate_limit", 100),
                    "output": "json"
                }
            ) as response:
                data = await response.json()
                return {
                    'text': str(data.get("response", {}).get("docs", [])),
                    'metadata': {'source': 'internet_archive'}
                }
        except Exception as e:
            self.logger.error(f"Erreur collecte Archive: {str(e)}")
            return {}

    async def _collect_from_github(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Collecte les données depuis GitHub"""
        try:
            async with self.session.get(
                "https://api.github.com/search/repositories",
                params={
                    "q": " OR ".join(self.search_queries),
                    "per_page": config.get("rate_limit", 100)
                }
            ) as response:
                data = await response.json()
                return {
                    'text': str(data.get("items", [])),
                    'metadata': {'source': 'github'}
                }
        except Exception as e:
            self.logger.error(f"Erreur collecte GitHub: {str(e)}")
            return {}

    async def stop(self) -> None:
        """Arrête la collecte continue"""
        self.running = False
        if self.session:
            await self.session.close()
