import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml

from ..memory.memory_manager import MemoryManager
from ..core.security_controller import SecurityController
from .collector import DataCollector
from .connectors import (
    GitHubConnector, 
    StackOverflowConnector,
    ArxivConnector,
    IEEEConnector,
    KaggleConnector
)

class SourceManagerError(Exception):
    def __init__(self, message: str, error_code: int = None):
        self.error_code = error_code
        super().__init__(f"[{error_code}] {message}" if error_code else message)

class SourceManager:
    """
    Gestionnaire des sources de données.
    
    Ce module charge la configuration des sources depuis le fichier YAML, crée les connecteurs correspondants,
    et fournit des méthodes pour obtenir et valider les informations de chaque source.
    """
    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        self.logger = logging.getLogger(__name__)
        self.memory_manager = memory_manager or MemoryManager()
        self.config = self._load_config()
        self.security_controller = SecurityController()
        self.active_sources: Dict[str, object] = {}  # Mapping source_id -> instance de connecteur
        self.metrics: Dict[str, Any] = {}            # Pour stocker les métriques globales
        self.collectors: Dict[str, DataCollector] = {}  # Si des collecteurs dynamiques sont utilisés

    def _default_config(self) -> Dict:
        """Renvoie la configuration par défaut pour la gestion des sources."""
        return {
            'version': "1.0.0",
            'max_sources': 10,
            'max_collectors': 5,
            'source_timeout': 30,
            'retry_attempts': 3,
            'retry_delay': 5,
            'batch_size': 100,
            'max_workers': 4,
            'sources': {
                'internet_archive': {
                    'enabled': True,
                    'priority': 1,
                    'rate_limit': 100,
                    'auth_required': False
                },
                'github': {
                    'enabled': True,
                    'priority': 2,
                    'rate_limit': 5000,
                    'auth_required': True
                },
                'stackoverflow': {
                    'enabled': True,
                    'priority': 3,
                    'rate_limit': 300,
                    'auth_required': True
                },
                'arxiv': {
                    'enabled': True,
                    'priority': 4,
                    'rate_limit': 100,
                    'auth_required': False
                },
                'ieee': {
                    'enabled': True,
                    'priority': 5,
                    'rate_limit': 100,
                    'auth_required': True
                },
                'kaggle': {
                    'enabled': True,
                    'priority': 6,
                    'rate_limit': 100,
                    'auth_required': True
                },
                'local_storage': {
                    'enabled': True,
                    'priority': 7,
                    'path': 'data/local'
                }
            },
            'security': {
                'max_requests_per_second': 1000,
                'max_memory_usage': 0.7,
                'encryption_enabled': True,
                'api_key_required': True
            }
        }

    def _validate_config(self, config: Dict) -> Dict:
        """
        Valide la configuration en vérifiant que la section 'sources' existe.
        Vous pouvez étendre cette validation si besoin.
        """
        if "sources" not in config:
            self.logger.warning("La configuration ne contient pas de section 'sources'. Utilisation des valeurs par défaut.")
            return self._default_config()
        return config

    def _load_config(self) -> Dict:
        """Charge la configuration depuis le fichier config/config.yml ou utilise la conf par défaut."""
        try:
            config_path = Path("config/config.yml")
            if config_path.exists():
                with open(config_path, "r") as f:
                    config = yaml.safe_load(f)
                    return self._validate_config(config)
            else:
                self.logger.warning("Fichier config/config.yml introuvable. Utilisation de la configuration par défaut.")
                return self._default_config()
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la configuration : {str(e)}. Utilisation de la configuration par défaut.")
            return self._default_config()

    async def load_sources(self) -> None:
        """
        Parcourt la configuration et instancie les connecteurs pour chaque source activée.
        Les connecteurs créés sont stockés dans self.active_sources.
        """
        sources_config = self.config.get('sources', {})
        for source_id, source_conf in sources_config.items():
            if source_conf.get('enabled', False):
                try:
                    connector = await self._create_source(source_id, source_conf)
                    self.active_sources[source_id] = connector
                    self.logger.info(f"Source '{source_id}' chargée avec succès.")
                except Exception as e:
                    self.logger.error(f"Impossible de charger la source '{source_id}': {str(e)}")

    async def _create_source(self, source_id: str, source_config: Dict) -> object:
        """
        Crée et retourne une instance de connecteur pour une source donnée.
        
        Args:
            source_id: Identifiant de la source dans la configuration.
            source_config: Configuration spécifiée pour cette source.
            
        Returns:
            Une instance de connecteur correspondant.
            
        Lève SourceManagerError en cas d’erreur.
        """
        try:
            source_type = source_config.get('type', '').lower()
            connector_map = {
                'github': GitHubConnector,
                'stackoverflow': StackOverflowConnector,
                'arxiv': ArxivConnector,
                'ieee': IEEEConnector,
                'kaggle': KaggleConnector,
            }
            
            if source_type not in connector_map:
                raise SourceManagerError(f"Type de source inconnu: {source_type}")
            
            # Vérifiez la présence d'une clé API si nécessaire.
            if self.config['sources'][source_type].get('auth_required'):
                if not source_config.get('api_key'):
                    raise SourceManagerError(f"Clé API requise pour {source_type}")
            
            connector_class = connector_map[source_type]
            connector = connector_class()
            
            # Si le connecteur possède une méthode de configuration, appelez-la.
            if hasattr(connector, 'configure'):
                await connector.configure(source_config)
                
            return connector
            
        except Exception as e:
            self.logger.error(f"Erreur création source '{source_id}': {str(e)}")
            raise SourceManagerError(f"Erreur création source '{source_id}': {str(e)}")

    async def get_source_info(self, source_id: str) -> Dict[str, Any]:
        """
        Retourne les informations détaillées d'une source active (type, configuration, statut, métriques, etc.).
        
        Args:
            source_id: Identifiant de la source.
            
        Returns:
            Un dictionnaire d'informations sur la source.
        """
        try:
            if source_id not in self.active_sources:
                raise SourceManagerError(f"Source inconnue: {source_id}")
            
            source = self.active_sources[source_id]
            source_config = self.config['sources'].get(source_id, {})
            
            info = {
                'id': source_id,
                'type': source.__class__.__name__,
                'enabled': source_config.get('enabled', False),
                'priority': source_config.get('priority', 0),
                'rate_limit': source_config.get('rate_limit', 0),
                'status': 'active' if source_id in self.collectors else 'idle',
                'metrics': {
                    'requests': self.metrics.get(f'{source_id}_requests', 0),
                    'errors': self.metrics.get(f'{source_id}_errors', 0),
                    'data_collected': self.metrics.get(f'{source_id}_data', 0)
                }
            }
            return info
            
        except Exception as e:
            self.logger.error(f"Erreur obtenu des infos pour la source '{source_id}': {str(e)}")
            raise SourceManagerError(f"Erreur info source '{source_id}': {str(e)}")

    async def get_all_sources(self) -> List[Dict[str, Any]]:
        """
        Retourne une liste d'informations pour toutes les sources actives.
        """
        infos = []
        for source_id in self.active_sources:
            try:
                info = await self.get_source_info(source_id)
                infos.append(info)
            except Exception as e:
                self.logger.error(f"Erreur obtenant les infos pour la source '{source_id}': {str(e)}")
        return infos

    async def validate_source_config(self, source_config: Dict) -> bool:
        """
        Valide la configuration d'une source.
        
        Args:
            source_config: Dictionnaire de configuration pour une source.
            
        Returns:
            True si la configuration est valide, sinon False.
        """
        try:
            required_fields = ['type', 'enabled', 'priority']
            for field in required_fields:
                if field not in source_config:
                    return False
            source_type = source_config['type'].lower()
            if source_type not in self.config['sources']:
                return False
            if self.config['sources'][source_type].get('auth_required'):
                if 'api_key' not in source_config:
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Erreur validation configuration source: {str(e)}")
            return False

    async def configure_source(self, source_id: str, new_config: Dict) -> None:
        """
        Met à jour la configuration d'une source existante.
        
        Args:
            source_id: Identifiant de la source à mettre à jour.
            new_config: Nouveau dictionnaire de configuration.
        """
        try:
            if source_id not in self.active_sources:
                raise SourceManagerError(f"Source inconnue: {source_id}")
            connector = self.active_sources[source_id]
            if hasattr(connector, 'configure'):
                await connector.configure(new_config)
            self.config['sources'][source_id] = new_config
            self.logger.info(f"Source '{source_id}' reconfigurée avec succès.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la configuration de la source '{source_id}': {str(e)}")
            raise SourceManagerError(f"Erreur configuration source '{source_id}': {str(e)}")

