
import unittest

from spaced_repetition.domain.problem import Difficulty, ProblemCreator
from spaced_repetition.presenters.cli_presenter import CliPresenter


class TestCliPresenter(unittest.TestCase):
    def test_problem_confirmation_txt(self):
        problem = ProblemCreator.create_problem(
            name='testname',
            difficulty=Difficulty(1),
            tags=['test-tag'],
            url='test-url')
        self.assertEqual("Created Problem 'testname' (difficulty 'EASY', "
                         "tags: test-tag)",
                         CliPresenter._problem_confirmation_txt(problem=problem))

    def test_format_entry(self):
        self.assertEqual(CliPresenter._format_entry(entry='123', max_len=5),
                         '123  ')

    def test_format_table_row(self):
        self.assertEqual(
            CliPresenter._format_table_row(
                content=['0123456789', '0123456789', '0123456789', '0123456789']),
            '| 0123456789           | 0123456789           | 0123456789 '
            '| 0123456789                |')

    def test_format_table_row_raises(self):
        with self.assertRaises(ValueError) as context:
            CliPresenter._format_table_row(content=[])

        self.assertEqual(str(context.exception),
                         'Need exactly 4 entries!')
