class InvalidAuthorizationHeader(Exception):
    def __init__(self, message: str = "Invalid authorization header"):
        self.message = message
        super().__init__(self.message)
