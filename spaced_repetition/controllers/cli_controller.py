"""Command line controller / user interface"""

import argparse

from spaced_repetition.domain.problem import Difficulty
from spaced_repetition.gateways.django_gateway.django_gateway import DjangoGateway
from spaced_repetition.presenters.cli_presenter import CliPresenter
from spaced_repetition.use_cases.add_problem import ProblemAdder
from spaced_repetition.use_cases.get_problem import ProblemGetter


class CliController:
    DESCRIPTION = """This is the command line interface to 'spaced_repetition'."""

    def __init__(self):
        self.command_mapper = {
            'create-problem': self._add_problem,
            'list-problems': self._list_problems}

        # add shortcuts
        self.command_mapper['cp'] = self.command_mapper['create-problem']
        self.command_mapper['l'] = self.command_mapper['list-problems']

    def run(self):
        args = self._parse_args()

        # execute command
        self.command_mapper[args.command]()

    @classmethod
    def _add_problem(cls):
        prob_adder = ProblemAdder(db_gateway=DjangoGateway(),
                                  presenter=CliPresenter())
        user_input = cls._record_problem_data()
        try:
            prob_adder.add_problem(
                difficulty=user_input['difficulty'],
                url=user_input['url'],
                name=user_input['name'],
                tags=user_input['tags'])
        except ValueError as err:
            print(err)
            return

    @staticmethod
    def _format_difficulty(difficulty: str):
        return Difficulty(int(difficulty))

    @staticmethod
    def _format_tags(tags: str):
        return tags.split()

    @staticmethod
    def _list_problems(limit: int = None):
        prob_getter = ProblemGetter(db_gateway=DjangoGateway(),
                                    presenter=CliPresenter())
        prob_getter.list_problems()

    def _parse_args(self):
        parser = argparse.ArgumentParser(description=CliController.DESCRIPTION)
        parser.add_argument('command', choices=self.command_mapper.keys())
        return parser.parse_args()

    @classmethod
    def _record_problem_data(cls) -> dict:
        sorted_difficulties = list(sorted([diff for diff in Difficulty],
                                          key=lambda d: d.value))
        min_diff, max_diff = sorted_difficulties[0], sorted_difficulties[-1]
        return {
            'name': input("Problem name: "),
            'difficulty': cls._format_difficulty(
                input(f"Select a difficulty from {min_diff.value} ({min_diff.name})"
                      f" to {max_diff.value} ({max_diff.name}): ")),
            'url': input("Url (optional): "),
            'tags': cls._format_tags(
                input("Supply whitespace-separated tags (at least one): "))}


def main():
    cli = CliController()
    cli.run()


if __name__ == "__main__":
    main()
