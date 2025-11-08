class ExamNotFound(Exception):
    def __init__(self, message: str = "Exam not found"):
        self.message = message
        super().__init__(self.message)
