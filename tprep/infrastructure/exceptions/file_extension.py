class FileExtension(Exception):
    def __init__(self, message: str = "Unsupported file extension"):
        self.message = message
        super().__init__(self.message)
