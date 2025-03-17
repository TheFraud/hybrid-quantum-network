class SecurityController:
    def __init__(self) -> None:
        # Compteur des requêtes et limite autorisée
        self.request_count = 0
        self.request_limit = 100  # Ajustez ce seuil selon vos besoins

    def check_request_limit(self) -> None:
        """
        Incrémente le compteur de requêtes et lève une exception si la limite est dépassée.
        """
        self.request_count += 1
        if self.request_count > self.request_limit:
            raise Exception("Limite de requêtes dépassée. Veuillez réessayer plus tard.")

