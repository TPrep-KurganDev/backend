class FileDecode(Exception):
    def __init__(self, message: str = "Cant decode this file"):
        self.message = message
        super().__init__(self.message)
