import unittest

from spaced_repetition.use_cases.helpers import clean_name


class TestHelpers(unittest.TestCase):
    def test_clean_name_no_change(self):
        self.assertEqual(clean_name(name='test name'),
                         'test name')

    def test_clean_name_removes_whitespace(self):
        self.assertEqual(clean_name(name=' test name '),
                         'test name')
