class CardNotFound(Exception):
    def __init__(self, message: str = "Card not found"):
        self.message = message
        super().__init__(self.message)