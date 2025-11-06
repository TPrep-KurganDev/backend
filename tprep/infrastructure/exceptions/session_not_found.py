class SessionNotFound(Exception):
    def __init__(self, message: str = "Session not found"):
        self.message = message
        super().__init__(self.message)
