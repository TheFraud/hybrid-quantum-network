import logging
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

class EncryptionHandler:
    """
    Gère le chiffrement et le déchiffrement des données sensibles.

    Utilise l'algorithme Fernet pour un chiffrement symétrique fiable.
    """
    def __init__(self, key: Optional[bytes] = None):
        """
        Args:
            key (Optional[bytes]): Clé de chiffrement. Si non fournie, une clé sera générée automatiquement.
        """
        self.logger = logging.getLogger(__name__)
        if key:
            self.key = key
        else:
            self.key = Fernet.generate_key()
            self.logger.info("Clé de chiffrement générée automatiquement.")
        self.fernet = Fernet(self.key)

    def encrypt(self, data: str) -> bytes:
        """
        Crypte une chaîne de caractères.

        Args:
            data (str): Texte en clair à chiffrer.

        Returns:
            bytes: Donnée chiffrée.
        """
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            self.logger.debug("Donnée cryptée avec succès.")
            return encrypted_data
        except Exception as e:
            self.logger.error(f"Erreur lors du chiffrement : {str(e)}")
            raise

    def decrypt(self, token: bytes) -> str:
        """
        Décrypte une donnée chiffrée.

        Args:
            token (bytes): Donnée chiffrée.

        Returns:
            str: Texte en clair après décryptage.

        Raises:
            InvalidToken: Si le token est invalide.
        """
        try:
            decrypted_data = self.fernet.decrypt(token)
            self.logger.debug("Donnée décryptée avec succès.")
            return decrypted_data.decode()
        except InvalidToken as e:
            self.logger.error("Token invalide lors du décryptage.")
            raise
        except Exception as e:
            self.logger.error(f"Erreur lors du décryptage : {str(e)}")
            raise

