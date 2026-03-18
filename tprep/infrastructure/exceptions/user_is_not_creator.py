class UserIsNotEditor(Exception):
    def __init__(self, message: str = "User is not the editor"):
        self.message = message
        super().__init__(self.message)
