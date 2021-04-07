
import unittest
from unittest.mock import patch

from spaced_repetition.controllers.cli_controller import CliController
from spaced_repetition.domain.problem import Difficulty
from spaced_repetition.domain.problem_log import Result


class TestCliController(unittest.TestCase):
    def test_format_difficulty(self):
        self.assertEqual(CliController._format_difficulty(difficulty='1'),
                         Difficulty.EASY)

    def test_format_difficulty_unknown_difficulty(self):
        with self.assertRaises(ValueError) as context:
            CliController._format_difficulty(difficulty='0')

        self.assertEqual(str(context.exception),
                         "0 is not a valid Difficulty")

    def test_format_tags(self):
        self.assertEqual(['tag1', 'tag2'],
                         CliController._format_tags('tag1 tag2'))

    # ------------------------ test user input --------------------------
    @patch('builtins.input', return_value=' 0')
    def test_get_user_input_result(self, _):
        self.assertEqual(Result.NO_IDEA,
                         CliController._get_user_input_result())

    @patch('builtins.input', return_value='55 ')
    def test_get_user_input_result_raises_invalid_problem(self, _):
        with self.assertRaises(ValueError):
            CliController._get_user_input_result()

    @patch('builtins.input', return_value=' some_name ')
    def test_get_user_input_problem_name(self, _):
        self.assertEqual('some_name',
                         CliController._get_problem_name())

    def test_clean_name_no_change(self):
        self.assertEqual(CliController._clean_input(user_input='test name'),
                         'test name')

    def test_clean_name_removes_whitespace(self):
        self.assertEqual(CliController._clean_input(user_input=' test name '),
                         'test name')
