"""Command line controller / user interface"""

import argparse

from spaced_repetition.domain.problem import Difficulty
from spaced_repetition.domain.problem_log import Action, Result
from spaced_repetition.gateways.django_gateway.django_gateway import DjangoGateway
from spaced_repetition.presenters.cli_presenter import CliPresenter
from spaced_repetition.use_cases.add_problem import ProblemAdder
from spaced_repetition.use_cases.get_problem import ProblemGetter
from spaced_repetition.use_cases.log_problem import ProblemLogger


class CliController:
    DESCRIPTION = """This is the spaced-repetition CLI"""

    def __init__(self):
        self.command_mapper = {
            'add-problem': self._add_problem,
            'list-problems': self._list_problems,
            'log-problem': self._log_problem,
        }

        # add shortcuts
        self.command_mapper['add'] = self.command_mapper['add-problem']
        self.command_mapper['list'] = self.command_mapper['list-problems']
        self.command_mapper['log'] = self.command_mapper['log-problem']

    def run(self):
        args = self._parse_args()
        print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        print(type(args))
        print(vars(args))

        kwargs = {k: v for k, v in vars(args).items() if k not in self.command_mapper}

        # execute command
        self.command_mapper[args.command](**kwargs)

    @classmethod
    def _add_problem(cls):
        """Record a new problem"""
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
    def _list_problems(args):
        prob_getter = ProblemGetter(db_gateway=DjangoGateway(),
                                    presenter=CliPresenter())
        kwargs = {}
        if args.search:
            kwargs['name_substr'] = args.search
        if args.sorted_by:
            kwargs['sorted_by'] = args.sorted_by
        prob_getter.list_problems(**kwargs)

    @classmethod
    def _log_problem(cls):
        """Log the execution of a problem"""
        prob_logger = ProblemLogger(db_gateway=DjangoGateway(),
                                    presenter=CliPresenter())
        try:
            prob_logger.log_problem(
                action=cls._get_user_input_action(),
                problem_id=cls._get_user_input_problem_id(),
                result=cls._get_user_input_result())
        except ValueError as err:
            print(err)
            return

    @staticmethod
    def _get_user_input_action():
        print('The following Action options exist:')
        for a in Action:
            print(a.name, a.value)
        return input('Choose one (int): ')

    @staticmethod
    def _get_user_input_problem_id():
        problem_id = int(input('Problem id: '))
        if DjangoGateway.problem_exists(problem_id=problem_id):
            return problem_id
        raise ValueError(f'Problem with problem_id {problem_id} does not exist')

    @staticmethod
    def _get_user_input_result():
        print('The following Result options exist:')
        for r in Result:
            print(r.name, r.value)
        return input('Choose one (int): ')

    def _parse_args(self):
        parser = argparse.ArgumentParser(description=CliController.DESCRIPTION)
        parser.add_argument('command',
                            choices=self.command_mapper.keys())
        parser.add_argument('--search')
        parser.add_argument('--sorted_by')
        return parser.parse_args()

    @classmethod
    def _record_problem_data(cls) -> dict:
        sorted_difficulties = list(sorted([diff for diff in Difficulty],
                                          key=lambda d: d.value))
        min_diff, max_diff = sorted_difficulties[0], sorted_difficulties[-1]
        return {
            'name': input("Problem name: "),
            'difficulty': cls._format_difficulty(
                input(f"Choose a difficulty between {min_diff.value} ({min_diff.name})"
                      f" and {max_diff.value} ({max_diff.name}): ")),
            'url': input("Url (optional): "),
            'tags': cls._format_tags(
                input("Supply whitespace-separated tags (at least one): "))}


def main():
    cli = CliController()
    cli.run()


if __name__ == "__main__":
    main()
