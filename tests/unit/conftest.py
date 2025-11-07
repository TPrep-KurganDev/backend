import pytest
from unittest.mock import Mock, MagicMock, patch
from tests.unit.mock_data import USERS, EXAMS, CARDS, STATISTICS


@pytest.fixture
def mock_stat_repo():
    with patch('tprep.domain.exam_session.StatRepo.inc_mistakes') as mock:
        yield mock


@pytest.fixture(autouse=True)
def clear_session_factory():
    from tprep.domain.services.session_factory import SessionFactory
    SessionFactory.session_ids = {}
    yield
    SessionFactory.session_ids = {}


@pytest.fixture
def mock_db():
    mock = MagicMock()

    mock_query_result = MagicMock()
    mock_filter_result = MagicMock()

    mock.query.return_value = mock_query_result
    mock_query_result.filter.return_value = mock_filter_result
    mock_query_result.join.return_value = mock_filter_result
    mock_filter_result.filter.return_value = mock_filter_result
    mock_filter_result.order_by.return_value = mock_filter_result
    mock_filter_result.limit.return_value = mock_filter_result
    mock_filter_result.first.return_value = None
    mock_filter_result.all.return_value = []
    mock_filter_result.count.return_value = 0

    mock.commit.return_value = None
    mock.add.return_value = None
    mock.delete.return_value = None
    mock.refresh.return_value = None
    mock.rollback.return_value = None

    return mock


def create_user_mock(user_data: dict):
    from tprep.infrastructure.user.user import User

    user = Mock(spec=User)
    for key, value in user_data.items():
        setattr(user, key, value)
    return user


def create_exam_mock(exam_data: dict):
    from tprep.infrastructure.exam.exam import Exam

    exam = Mock(spec=Exam)
    for key, value in exam_data.items():
        setattr(exam, key, value)
    return exam


def create_card_mock(card_data: dict):
    from tprep.infrastructure.exam.exam import Card

    card = Mock(spec=Card)
    for key, value in card_data.items():
        setattr(card, key, value)
    return card


def create_statistic_mock(stat_data: dict):
    from tprep.infrastructure.statistic.statistic import Statistic

    stat = Mock(spec=Statistic)
    for key, value in stat_data.items():
        setattr(stat, key, value)
    return stat


@pytest.fixture(params=["default", "user_2", "admin"])
def user_config(request):
    return USERS[request.param]


@pytest.fixture
def mock_user_from_config(user_config):
    return create_user_mock(user_config)


@pytest.fixture
def mock_user():
    return create_user_mock(USERS["default"])


@pytest.fixture
def mock_user_2():
    return create_user_mock(USERS["user_2"])


@pytest.fixture(params=["default", "exam_2", "empty_exam"])
def exam_config(request):
    return EXAMS[request.param]


@pytest.fixture
def mock_exam_from_config(exam_config):
    return create_exam_mock(exam_config)


@pytest.fixture
def mock_exam():
    return create_exam_mock(EXAMS["default"])


@pytest.fixture
def mock_exam_2():
    return create_exam_mock(EXAMS["exam_2"])


@pytest.fixture(params=["exam_1_cards", "exam_2_cards"])
def cards_config(request):
    return CARDS[request.param]


@pytest.fixture
def mock_cards_from_config(cards_config):
    return [create_card_mock(card_data) for card_data in cards_config]


@pytest.fixture
def mock_cards():
    return [create_card_mock(card_data) for card_data in CARDS["exam_1_cards"]]


@pytest.fixture(params=["default", "high_mistakes", "no_mistakes"])
def statistic_config(request):
    return STATISTICS[request.param]


@pytest.fixture
def mock_statistic_from_config(statistic_config):
    return create_statistic_mock(statistic_config)


@pytest.fixture
def mock_statistic():
    return create_statistic_mock(STATISTICS["default"])