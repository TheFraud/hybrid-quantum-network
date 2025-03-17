import logging
from typing import List, Dict, Any, Optional

import usb.core
import usb.util


class USBController:
    """
    USBController

    Cette classe gère la détection, la connexion et la communication avec les périphériques USB.
    Elle permet d'énumérer les appareils connectés, d'établir une connexion et d'échanger des données.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connected_devices: List[usb.core.Device] = []

    def list_devices(self) -> List[Dict[str, Any]]:
        """
        Liste les périphériques USB connectés.

        Returns:
            List[Dict[str, Any]]: Une liste de dictionnaires contenant des informations (idVendor, idProduct, fabricant, produit, etc.).
        """
        devices = usb.core.find(find_all=True)
        device_list = []
        for dev in devices:
            try:
                dev_info = {
                    "idVendor": hex(dev.idVendor),
                    "idProduct": hex(dev.idProduct),
                    "manufacturer": usb.util.get_string(dev, dev.iManufacturer) if dev.iManufacturer else None,
                    "product": usb.util.get_string(dev, dev.iProduct) if dev.iProduct else None,
                    "serial_number": usb.util.get_string(dev, dev.iSerialNumber) if dev.iSerialNumber else None,
                }
            except Exception as e:
                self.logger.warning(f"Impossible de récupérer certaines informations pour un périphérique: {str(e)}")
                dev_info = {
                    "idVendor": hex(dev.idVendor),
                    "idProduct": hex(dev.idProduct),
                }
            device_list.append(dev_info)
        self.logger.info(f"{len(device_list)} périphériques USB trouvés.")
        return device_list

    def connect_device(self, idVendor: int, idProduct: int) -> Optional[usb.core.Device]:
        """
        Connecte un périphérique USB en fonction de son idVendor et idProduct.

        Args:
            idVendor (int): L'identifiant du vendeur.
            idProduct (int): L'identifiant du produit.

        Returns:
            Optional[usb.core.Device]: L'objet device si la connexion est réussie, sinon None.
        """
        try:
            dev = usb.core.find(idVendor=idVendor, idProduct=idProduct)
            if dev is None:
                self.logger.warning("Périphérique non trouvé.")
                return None

            # Si nécessaire, préparez le périphérique avant communication (ex: réinitialisation, configuration, etc.)
            self.connected_devices.append(dev)
            self.logger.info(f"Périphérique {hex(idVendor)}:{hex(idProduct)} connecté avec succès.")
            return dev
        except Exception as e:
            self.logger.error(f"Erreur lors de la connexion au périphérique USB: {str(e)}")
            return None

    def disconnect_device(self, device: usb.core.Device) -> bool:
        """
        Déconnecte le périphérique USB spécifié.

        Args:
            device (usb.core.Device): L'objet représentant le périphérique à déconnecter.

        Returns:
            bool: True si la déconnexion a été effectuée, False sinon.
        """
        try:
            if device in self.connected_devices:
                self.connected_devices.remove(device)
                usb.util.dispose_resources(device)
                self.logger.info("Périphérique déconnecté avec succès.")
                return True
            else:
                self.logger.warning("Périphérique non trouvé dans la liste des connexions.")
                return False
        except Exception as e:
            self.logger.error(f"Erreur lors de la déconnexion du périphérique USB: {str(e)}")
            return False

    def send_data(self, device: usb.core.Device, data: bytes, endpoint: int) -> bool:
        """
        Envoie des données au périphérique USB connecté.

        Args:
            device (usb.core.Device): Le périphérique cible.
            data (bytes): Les données à envoyer.
            endpoint (int): L'endpoint de sortie sur le périphérique.

        Returns:
            bool: True si l'envoi a réussi, False sinon.
        """
        try:
            device.write(endpoint, data)
            self.logger.info("Données envoyées avec succès via USB.")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de données via USB: {str(e)}")
            return False

    def read_data(
        self, device: usb.core.Device, endpoint: int, size: int, timeout: int = 1000
    ) -> Optional[bytes]:
        """
        Lit des données depuis le périphérique USB connecté.

        Args:
            device (usb.core.Device): Le périphérique cible.
            endpoint (int): L'endpoint de lecture.
            size (int): Le nombre d'octets à lire.
            timeout (int, optional): Temps d'attente en millisecondes. Defaults to 1000.

        Returns:
            Optional[bytes]: Les données lues sous forme de bytes, ou None en cas d'erreur.
        """
        try:
            data = device.read(endpoint, size, timeout=timeout)
            self.logger.info("Données lues avec succès depuis le périphérique USB.")
            return bytes(data)
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture des données via USB: {str(e)}")
            return None
