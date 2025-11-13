import pytest

from tprep.domain.exam_session import ExamSession
from tprep.infrastructure.exceptions.question_not_in_session import QuestionNotInSession


class TestExamSessionInitialization:
    def test_exam_session_initialization(self):
        user_id = 1
        exam_id = 10
        questions = [1, 2, 3, 4, 5]

        session = ExamSession(user_id, exam_id, questions)

        assert session.user_id == user_id
        assert session.exam_id == exam_id
        assert session.questions == questions

    def test_exam_session_with_empty_questions(self):
        session = ExamSession(1, 10, [])

        assert session.questions == []
        assert session.user_id == 1
        assert session.exam_id == 10

    def test_exam_session_unique_ids(self):
        session1 = ExamSession(1, 10, [1, 2, 3])
        session2 = ExamSession(1, 10, [1, 2, 3])

        assert session1.id != session2.id

    def test_exam_session_created_at_timestamp(self):
        session = ExamSession(1, 10, [1, 2, 3])

        assert hasattr(session, "created_at")


class TestExamSessionSetAnswer:
    def test_set_answer_correct_answer(self, mock_stat_repo, test_db):
        session = ExamSession(1, 10, [1, 2, 3])
        session._answers = {}

        session.set_answer(1, True, test_db)

        mock_stat_repo.assert_not_called()
        assert session._answers[1] is True

    def test_set_answer_incorrect_answer(self, mock_stat_repo, test_db):
        session = ExamSession(1, 10, [1, 2, 3])
        session._answers = {}

        session.set_answer(1, False, test_db)

        mock_stat_repo.assert_called_once_with(1, 1, test_db)
        assert session._answers[1] is False

    def test_set_answer_question_not_in_session(self, test_db):
        session = ExamSession(1, 10, [1, 2, 3])
        session._answers = {}

        with pytest.raises(QuestionNotInSession) as exc_info:
            session.set_answer(999, True, test_db)

        assert "Question 999 is not part of this session" in str(exc_info.value)

    def test_set_answer_multiple_questions(self, mock_stat_repo, test_db):
        session = ExamSession(1, 10, [1, 2, 3, 4])
        session._answers = {}

        session.set_answer(1, True, test_db)
        session.set_answer(2, False, test_db)
        session.set_answer(3, True, test_db)
        session.set_answer(4, False, test_db)

        # Two incorrect answers
        assert mock_stat_repo.call_count == 2

        # Check all answers were recorded
        assert session._answers[1] is True
        assert session._answers[2] is False
        assert session._answers[3] is True
        assert session._answers[4] is False

    def test_set_answer_can_overwrite_answer(self, mock_stat_repo, test_db):
        session = ExamSession(1, 10, [1, 2, 3])
        session._answers = {}

        # First answer: correct
        session.set_answer(1, True, test_db)
        assert session._answers[1] is True

        # Overwrite: incorrect
        session.set_answer(1, False, test_db)
        assert session._answers[1] is False

        # inc_mistakes should be called for the second (incorrect) answer
        mock_stat_repo.assert_called_once_with(1, 1, test_db)

    def test_set_answer_all_questions_in_session(self, mock_stat_repo, test_db):
        session = ExamSession(1, 10, [5, 10, 15])
        session._answers = {}

        # These should work
        session.set_answer(5, True, test_db)
        session.set_answer(10, False, test_db)
        session.set_answer(15, True, test_db)

        # These should raise exceptions
        with pytest.raises(QuestionNotInSession):
            session.set_answer(1, True, test_db)

        with pytest.raises(QuestionNotInSession):
            session.set_answer(20, True, test_db)

    def test_set_answer_increments_mistakes_with_correct_parameters(
        self, mock_stat_repo, test_db
    ):
        user_id = 42
        exam_id = 100
        question_id = 7
        session = ExamSession(user_id, exam_id, [question_id])
        session._answers = {}

        session.set_answer(question_id, False, test_db)

        # Verify inc_mistakes was called with correct user_id and question_id
        mock_stat_repo.assert_called_once_with(user_id, question_id, test_db)

    def test_set_answer_empty_session_raises_exception(self, test_db):
        session = ExamSession(1, 10, [])
        session._answers = {}

        with pytest.raises(QuestionNotInSession):
            session.set_answer(1, True, test_db)


class TestExamSessionAnswersTracking:
    def test_answers_dict_initially_empty(self, mock_stat_repo):
        session = ExamSession(1, 10, [1, 2, 3])
        session._answers = {}

        assert len(session._answers) == 0

    def test_answers_dict_populated_after_set_answer(self, mock_stat_repo, test_db):
        session = ExamSession(1, 10, [1, 2, 3])
        session._answers = {}

        session.set_answer(1, True, test_db)
        session.set_answer(2, False, test_db)

        assert len(session._answers) == 2
        assert 1 in session._answers
        assert 2 in session._answers

    def test_can_retrieve_specific_answer(self, mock_stat_repo, test_db):
        session = ExamSession(1, 10, [1, 2, 3])
        session._answers = {}

        session.set_answer(1, True, test_db)
        session.set_answer(2, False, test_db)

        assert session._answers[1] is True
        assert session._answers[2] is False
