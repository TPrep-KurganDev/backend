class AiGenerationFailed(Exception):
    def __init__(self, message: str = "AI answer generation failed"):
        self.message = message
        super().__init__(self.message)
