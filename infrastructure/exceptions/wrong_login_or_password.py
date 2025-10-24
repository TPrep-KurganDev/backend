class WrongLoginOrPassword(Exception):
    def __init__(self, message: str = "Wrong login or password"):
        self.message = message
        super().__init__(self.message)