class QuestionNotInSession(Exception):
    def __init__(self, message: str = "Question is not part of this session."):
        self.message = message
        super().__init__(self.message)