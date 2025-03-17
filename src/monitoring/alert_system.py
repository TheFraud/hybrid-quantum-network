import smtplib
import logging
from email.mime.text import MIMEText
from typing import Dict, Any

class AlertSystem:
    """
    Système d’alertes pour surveiller les métriques critiques du système.

    Permet d'envoyer des alertes par email lorsque certains seuils (par exemple, utilisation CPU ou mémoire)
    sont dépassés.
    """
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        recipient_email: str,
        cpu_threshold: float = 90.0,
        memory_threshold: float = 90.0
    ):
        self.logger = logging.getLogger(__name__)
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold

    def send_email_alert(self, subject: str, message: str) -> None:
        """
        Envoie une alerte par email.

        Args:
            subject (str): Le sujet de l'email.
            message (str): Le contenu de l'alerte.
        """
        try:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            self.logger.info("Alerte envoyée par email.")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'alerte email : {str(e)}")

    def check_metrics_and_alert(self, metrics: Dict[str, Any]) -> None:
        """
        Vérifie les métriques et déclenche une alerte si les seuils sont dépassés.

        Args:
            metrics (dict): Dictionnaire contenant par exemple 'cpu_percent' et 'memory' (avec 'percent').
        """
        try:
            cpu_usage = metrics.get('cpu_percent')
            memory_info = metrics.get('memory', {})
            memory_usage = memory_info.get('percent')

            alert_message = ""
            if cpu_usage and cpu_usage > self.cpu_threshold:
                alert_message += f"Utilisation du CPU critique : {cpu_usage}%\n"
            if memory_usage and memory_usage > self.memory_threshold:
                alert_message += f"Utilisation de la mémoire critique : {memory_usage}%\n"
            if alert_message:
                subject = "Alerte Système Quantum AI"
                self.send_email_alert(subject, alert_message)
                self.logger.info("Alerte envoyée : " + alert_message)
            else:
                self.logger.info("Aucune alerte : métriques sous seuil.")
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification des métriques : {str(e)}")

