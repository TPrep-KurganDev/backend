class InvalidOrExpiredToken(Exception):
    def __init__(self, message: str = "Invalid or expired refresh token"):
        self.message = message
        super().__init__(self.message)
