class FileParsing(Exception):
    def __init__(self, message: str = "Error with parsing of file"):
        self.message = message
        super().__init__(self.message)
