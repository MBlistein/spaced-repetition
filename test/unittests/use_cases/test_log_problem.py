import datetime as dt
import unittest
from unittest.mock import Mock

from spaced_repetition.domain.problem_log import (ProblemLogCreator, Result)
from spaced_repetition.use_cases.log_problem import ProblemLogger


class TestProblemAdder(unittest.TestCase):
    def test_get_last_log_for_problem(self):
        pl_1 = ProblemLogCreator.create(
            last_log=None,
            problem_id=1,
            result=Result.NO_IDEA,
            timestamp=dt.datetime(2021, 3, 19))
        pl_2 = ProblemLogCreator.create(
            last_log=None,
            problem_id=1,
            result=Result.NO_IDEA,
            timestamp=dt.datetime(2021, 3, 20))

        mock_gateway = Mock()
        mock_gateway.get_problem_logs.return_value = [pl_2, pl_1]

        p_l = ProblemLogger(db_gateway=mock_gateway, presenter=Mock())
        self.assertEqual(pl_2,
                         p_l.get_last_log_for_problem(problem_id=1))

    def test_get_last_log_for_problem_no_log_found(self):
        mock_gateway = Mock()
        mock_gateway.get_problem_logs.return_value = []

        p_l = ProblemLogger(db_gateway=mock_gateway, presenter=Mock())
        self.assertEqual(None,
                         p_l.get_last_log_for_problem(problem_id=1))
