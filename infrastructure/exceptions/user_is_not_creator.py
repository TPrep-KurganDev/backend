class UserIsNotCreator(Exception):
    def __init__(self, message: str = "User is not the creator"):
        self.message = message
        super().__init__(self.message)