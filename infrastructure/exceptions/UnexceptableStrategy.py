class UnexceptableStrategy(Exception):
    def __init__(self, message: str = "Unknow strategy"):
        self.message = message
        super().__init__(self.message)