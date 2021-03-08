
import unittest

from spaced_repetition.domain.domain_helpers import validate_input


class TestDomainHelpers(unittest.TestCase):
    def test_validate_input(self):
        self.assertEqual(validate_input(inpt='valid name',
                                        max_length=10),
                         'valid name')

    def test_validate_input_raises_wrong_type(self):
        with self.assertRaises(TypeError) as context:
            validate_input(inpt=3, max_length=10)

        self.assertEqual(str(context.exception),
                         f"Input should by of type 'str', but is of type {int}")

    def test_validate_input_raises_empty(self):
        with self.assertRaises(ValueError) as context:
            validate_input(inpt='', max_length=10)

        self.assertEqual(str(context.exception),
                         "Input cannot be empty.")

    def test_validate_input_raises_too_long(self):
        with self.assertRaises(ValueError) as context:
            validate_input(inpt='12345', max_length=4, label='TestLabel')

        self.assertEqual(str(context.exception),
                         f"TestLabel too long, max length = 4 chars.")

    def test_validate_name_raises_whitespace_on_end(self):
        with self.assertRaises(ValueError) as context:
            validate_input(inpt=' before', max_length=10, label='TestLabel')

        self.assertEqual(str(context.exception),
                         f"Error: TestLabel ' before' has whitespace on either end.")

        with self.assertRaises(ValueError) as context:
            validate_input(inpt='after ', max_length=10, label='TestLabel')

        self.assertEqual(str(context.exception),
                         f"Error: TestLabel 'after ' has whitespace on either end.")
