import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass

import aiohttp
import websockets
import requests
import arxiv
import kaggle
from ieee_api import XPLORE  # Assurez-vous que ce module est disponible
from bs4 import BeautifulSoup

# Définition d'une classe de base pour les connecteurs
class BaseConnector(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def fetch_data(self, query: str) -> Dict:
        pass

    @abstractmethod
    async def process_data(self, data: Dict) -> Dict:
        pass

@dataclass
class ConnectionConfig:
    api_key: Optional[str] = None
    # D'autres paramètres de configuration peuvent être ajoutés si nécessaire.

# Connecteur pour Internet Archive
class InternetArchiveConnector(BaseConnector):
    async def fetch_data(self, query: str, max_results: int = 50) -> Dict:
        try:
            import internetarchive as ia
        except ImportError as e:
            self.logger.error("Module internetarchive manquant.")
            return {}
        search = ia.search_items(query)
        items = []
        for i, result in enumerate(search):
            if i >= max_results:
                break
            item = ia.get_item(result['identifier'])
            items.append(item.metadata)
        return {"items": items}

    async def process_data(self, data: Dict) -> Dict:
        try:
            if "items" in data:
                return {
                    "status": "success",
                    "data": data["items"]
                }
            return {"status": "error", "message": "Format de données invalide"}
        except Exception as e:
            self.logger.error(f"InternetArchive process error: {str(e)}")
            return {"status": "error", "message": str(e)}

# Connecteur GitHub
class GitHubConnector(BaseConnector):
    def __init__(self):
        super().__init__()
        self.api_token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.api_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def fetch_data(self, query: str) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search/code",
                    params={"q": query},
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"GitHub response status: {response.status}")
                        return {}
        except Exception as e:
            self.logger.error(f"GitHub error: {str(e)}")
            return {}

    async def process_data(self, data: Dict) -> Dict:
        try:
            if "items" in data:
                return {
                    "status": "success",
                    "data": [{
                        "name": item.get("name", ""),
                        "path": item.get("path", ""),
                        "url": item.get("html_url", ""),
                        "repository": item.get("repository", {}).get("full_name", ""),
                        "score": item.get("score", 0)
                    } for item in data["items"]]
                }
            return {"status": "error", "message": "Format de données invalide"}
        except Exception as e:
            self.logger.error(f"GitHub process error: {str(e)}")
            return {"status": "error", "message": str(e)}

# Connecteur StackOverflow
class StackOverflowConnector(BaseConnector):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("STACKOVERFLOW_KEY")
        self.base_url = "https://api.stackexchange.com/2.3"

    async def fetch_data(self, query: str) -> Dict:
        try:
            params = {
                "site": "stackoverflow",
                "key": self.api_key,
                "order": "desc",
                "sort": "votes",
                "intitle": query,
                "filter": "withbody"
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/search/advanced", params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"StackOverflow response status: {response.status}")
                        return {}
        except Exception as e:
            self.logger.error(f"StackOverflow error: {str(e)}")
            return {}

    async def process_data(self, data: Dict) -> Dict:
        try:
            if "items" in data:
                return {
                    "status": "success",
                    "data": [{
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "score": item.get("score", 0),
                        "answers": item.get("answer_count", 0),
                        "accepted": item.get("is_answered", False)
                    } for item in data["items"]]
                }
            return {"status": "error", "message": "Format de données invalide"}
        except Exception as e:
            self.logger.error(f"StackOverflow process error: {str(e)}")
            return {"status": "error", "message": str(e)}

# Connecteur arXiv
class ArxivConnector(BaseConnector):
    def __init__(self):
        super().__init__()
        self.client = arxiv.Client()

    async def fetch_data(self, query: str) -> Dict:
        try:
            search = arxiv.Search(
                query=query,
                max_results=50,
                sort_by=arxiv.SortCriterion.Relevance
            )
            results = await asyncio.to_thread(list, self.client.results(search))
            return {"items": results}
        except Exception as e:
            self.logger.error(f"arXiv error: {str(e)}")
            return {}

    async def process_data(self, data: Dict) -> Dict:
        try:
            if "items" in data:
                return {
                    "status": "success",
                    "data": [{
                        "title": result.title,
                        "authors": [author.name for author in result.authors],
                        "summary": result.summary,
                        "published": result.published.isoformat() if result.published else "",
                        "pdf_url": result.pdf_url
                    } for result in data["items"]]
                }
            return {"status": "error", "message": "Format de données invalide"}
        except Exception as e:
            self.logger.error(f"arXiv process error: {str(e)}")
            return {"status": "error", "message": str(e)}

# Connecteur IEEE
class IEEEConnector(BaseConnector):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("IEEE_API_KEY")
        self.xplore = XPLORE(self.api_key)

    async def fetch_data(self, query: str) -> Dict:
        try:
            results = await asyncio.to_thread(
                self.xplore.search,
                querytext=query,
                max_records=50
            )
            return results
        except Exception as e:
            self.logger.error(f"IEEE error: {str(e)}")
            return {}

    async def process_data(self, data: Dict) -> Dict:
        try:
            if "articles" in data:
                return {
                    "status": "success",
                    "data": [{
                        "title": article.get("title", ""),
                        "authors": article.get("authors", []),
                        "doi": article.get("doi", ""),
                        "publication": article.get("publication_title", ""),
                        "abstract": article.get("abstract", "")
                    } for article in data["articles"]]
                }
            return {"status": "error", "message": "Format de données invalide"}
        except Exception as e:
            self.logger.error(f"IEEE process error: {str(e)}")
            return {"status": "error", "message": str(e)}

# Connecteur Kaggle
class KaggleConnector(BaseConnector):
    def __init__(self):
        super().__init__()
        self.api = kaggle.KaggleApi()
        self.api.authenticate()

    async def fetch_data(self, query: str) -> Dict:
        try:
            datasets = await asyncio.to_thread(
                self.api.dataset_list,
                search=query
            )
            return {"items": datasets}
        except Exception as e:
            self.logger.error(f"Kaggle error: {str(e)}")
            return {}

    async def process_data(self, data: Dict) -> Dict:
        try:
            if "items" in data:
                return {
                    "status": "success",
                    "data": [{
                        "title": dataset.title,
                        "size": dataset.size,
                        "lastUpdated": dataset.lastUpdated,
                        "downloadCount": dataset.downloadCount,
                        "url": f"https://www.kaggle.com/{dataset.ref}"
                    } for dataset in data["items"]]
                }
            return {"status": "error", "message": "Format de données invalide"}
        except Exception as e:
            self.logger.error(f"Kaggle process error: {str(e)}")
            return {"status": "error", "message": str(e)}

# Connecteur REST (stub)
class RESTConnector(BaseConnector):
    def __init__(self, config: Optional[ConnectionConfig] = None):
        super().__init__()
        self.config = config

    async def fetch_data(self, query: str) -> Dict:
        # Implémentez la logique REST ici si nécessaire
        return {}

    async def process_data(self, data: Dict) -> Dict:
        return {}

# Connecteur WebSocket (stub)
class WebSocketConnector(BaseConnector):
    def __init__(self, config: Optional[ConnectionConfig] = None):
        super().__init__()
        self.config = config

    async def fetch_data(self, query: str) -> Dict:
        # Implémentez la logique WebSocket ici si nécessaire
        return {}

    async def process_data(self, data: Dict) -> Dict:
        return {}

# DataConnectorFactory pour choisir le connecteur approprié
class DataConnectorFactory:
    @staticmethod
    def get_connector(connector_type: str, config: Optional[ConnectionConfig] = None) -> BaseConnector:
        connectors = {
            "archive": InternetArchiveConnector,
            "github": GitHubConnector,
            "stackoverflow": StackOverflowConnector,
            "arxiv": ArxivConnector,
            "ieee": IEEEConnector,
            "kaggle": KaggleConnector,
            "rest": lambda: RESTConnector(config) if config else None,
            "websocket": lambda: WebSocketConnector(config) if config else None
        }
        
        connector_class = connectors.get(connector_type.lower())
        if connector_class:
            if isinstance(connector_class, type):
                return connector_class()
            return connector_class()
        else:
            raise ValueError(f"Unknown connector type: {connector_type}")

