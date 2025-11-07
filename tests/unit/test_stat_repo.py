import pytest
from unittest.mock import Mock, MagicMock

from tprep.infrastructure.statistic.statistic import Statistic
from tprep.infrastructure.statistic.stat_repo import StatRepo


class TestStatRepoIncMistakes:
    def test_inc_mistakes_increments_existing_statistic(self, mock_db):
        class MockStat:
            def __init__(self):
                self.user_id = 1
                self.card_id = 1
                self.mistakes_count = 5

        mock_stat = MockStat()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_stat

        StatRepo.inc_mistakes(1, 1, mock_db)

        assert mock_stat.mistakes_count == 6
        mock_db.commit.assert_called_once()

    def test_inc_mistakes_creates_new_statistic_when_not_exists(self, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = None

        StatRepo.inc_mistakes(1, 10, mock_db)

        assert mock_db.add.called
        mock_db.commit.assert_called_once()

    def test_inc_mistakes_increments_multiple_times(self, mock_db):
        class MockStat:
            def __init__(self):
                self.user_id = 1
                self.card_id = 1
                self.mistakes_count = 5

        mock_stat = MockStat()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_stat

        for _ in range(3):
            StatRepo.inc_mistakes(1, 1, mock_db)

        assert mock_stat.mistakes_count == 8
        assert mock_db.commit.call_count == 3

    def test_inc_mistakes_different_users_separate_statistics(self, mock_db):
        class MockStat:
            def __init__(self):
                self.user_id = 1
                self.card_id = 1
                self.mistakes_count = 5

        mock_stat1 = MockStat()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_stat1

        StatRepo.inc_mistakes(1, 1, mock_db)

        assert mock_stat1.mistakes_count == 6
        mock_db.query.assert_called()
        mock_db.commit.assert_called()