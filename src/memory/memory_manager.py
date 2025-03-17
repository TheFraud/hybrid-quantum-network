import sqlite3
from typing import Dict, Any, List, Optional
import json
import logging
from pathlib import Path
import time

class MemoryManager:
    def __init__(self, db_path: str = "data/memory.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = Path(db_path)
        # Assurer que le dossier contenant la base existe
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.setup_database()

    def setup_database(self):
        """Initialise la base de données SQLite pour stocker les données."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memory (
                        id INTEGER PRIMARY KEY,
                        type TEXT,
                        content TEXT,
                        metadata TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS embeddings (
                        id INTEGER PRIMARY KEY,
                        memory_id INTEGER,
                        embedding BLOB,
                        FOREIGN KEY(memory_id) REFERENCES memory(id)
                    )
                """)
            self.logger.info("Base de données initialisée avec succès")
        except Exception as e:
            self.logger.error(f"Erreur d'initialisation de la base de données: {str(e)}")
            raise

    def store(self, data_type: str, content: Dict[str, Any], 
              metadata: Optional[Dict] = None) -> int:
        """
        Stocke des données dans la base SQLite.

        Args:
            data_type (str): Le type de données à stocker.
            content (dict): Le contenu à stocker.
            metadata (dict, optionnel): Métadonnées associées.
            
        Returns:
            int: L'ID de la ligne insérée.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO memory (type, content, metadata) VALUES (?, ?, ?)",
                    (data_type, json.dumps(content), 
                     json.dumps(metadata) if metadata else None)
                )
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Erreur de stockage: {str(e)}")
            raise

    def retrieve(self, data_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Récupère des données stockées.

        Args:
            data_type (str, optionnel): Filtre sur le type de données.
            limit (int): Nombre maximum de résultats.
            
        Returns:
            List[dict]: Une liste de résultats.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if data_type:
                    query = """
                        SELECT id, type, content, metadata, timestamp 
                        FROM memory WHERE type = ? ORDER BY timestamp DESC LIMIT ?
                    """
                    cursor.execute(query, (data_type, limit))
                else:
                    query = """
                        SELECT id, type, content, metadata, timestamp 
                        FROM memory ORDER BY timestamp DESC LIMIT ?
                    """
                    cursor.execute(query, (limit,))
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'id': row[0],
                        'type': row[1],
                        'content': json.loads(row[2]),
                        'metadata': json.loads(row[3]) if row[3] else None,
                        'timestamp': row[4]
                    })
                return results
        except Exception as e:
            self.logger.error(f"Erreur de récupération: {str(e)}")
            raise

    def clear(self, older_than_days: Optional[int] = None):
        """
        Supprime les données stockées.

        Args:
            older_than_days (int, optionnel): Supprime les données plus anciennes que ce nombre de jours.
            Sans ce paramètre, supprime toutes les données.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                if older_than_days:
                    timestamp = time.time() - (older_than_days * 24 * 3600)
                    conn.execute(
                        "DELETE FROM memory WHERE timestamp < datetime(?)",
                        (timestamp,)
                    )
                else:
                    conn.execute("DELETE FROM memory")
            self.logger.info("Nettoyage de la mémoire effectué")
        except Exception as e:
            self.logger.error(f"Erreur de nettoyage: {str(e)}")
            raise

