class ExamHasNoCards(Exception):
    def __init__(self, message: str = "Exam has no cards."):
        self.message = message
        super().__init__(self.message)
