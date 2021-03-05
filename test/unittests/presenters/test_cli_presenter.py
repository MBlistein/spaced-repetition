
import unittest
from unittest.mock import call, Mock

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.presenters.cli_presenter import CliPresenter


PROBLEM = ProblemCreator.create_problem(
    name='testname',
    difficulty=Difficulty(1),
    problem_id=1,
    tags=['test-tag'],
    url='test-url')


class TestCliPresenter(unittest.TestCase):
    def test_problem_confirmation_txt(self):
        self.assertEqual("Created Problem 'testname' with id '1' "
                         "(difficulty 'EASY', tags: test-tag)",
                         CliPresenter._problem_confirmation_txt(problem=PROBLEM))

    def test_format_entry(self):
        self.assertEqual(CliPresenter._format_entry(entry='123', max_len=5),
                         '123  ')

    def test_format_table_row(self):
        self.assertEqual(
            CliPresenter._format_table_row(
                content=['01234', '0123456789', '0123456789', '0123456789', '0123456789']),
            '| 01234 | 0123456789           | 0123456789           | 0123456789 '
            '| 0123456789                |')

    def test_format_table_row_raises(self):
        with self.assertRaises(ValueError) as context:
            CliPresenter._format_table_row(content=[])

        self.assertEqual(str(context.exception),
                         'Need exactly 5 entries!')

    def test_list_problems(self):
        class FakePresenter(CliPresenter):
            pass

        presenter = FakePresenter
        presenter._format_table_row = Mock()

        presenter.list_problems(problems=[PROBLEM, PROBLEM])

        calls = [
            call(content=['Id', 'Name', 'Tags', 'Difficulty', 'URL']),
            call(content=['1', 'testname', 'test-tag', 'EASY', 'test-url']),
            call(content=['1', 'testname', 'test-tag', 'EASY', 'test-url']),
        ]
        presenter._format_table_row.assert_has_calls(calls)
