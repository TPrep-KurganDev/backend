class WrongNValue(Exception):
    def __init__(self, message: str = "Wrong n value"):
        self.message = message
        super().__init__(self.message)
