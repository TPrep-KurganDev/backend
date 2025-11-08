class UserAlreadyExists(Exception):
    def __init__(self, message: str = "User already exists"):
        self.message = message
        super().__init__(self.message)
