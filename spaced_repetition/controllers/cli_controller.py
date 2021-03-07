"""Command line controller / user interface"""

import argparse

from spaced_repetition.domain.problem import Difficulty
from spaced_repetition.domain.problem_log import Action, Result
from spaced_repetition.gateways.django_gateway.django_gateway import DjangoGateway
from spaced_repetition.presenters.cli_presenter import CliPresenter
from spaced_repetition.use_cases.add_problem import ProblemAdder
from spaced_repetition.use_cases.add_tag import TagAdder
from spaced_repetition.use_cases.get_problem import ProblemGetter
from spaced_repetition.use_cases.log_problem import ProblemLogger


class CliController:
    DESCRIPTION = """This is the spaced-repetition CLI"""

    @classmethod
    def run(cls):
        args = cls._parse_args()
        args.func(args)

    @classmethod
    def _parse_args(cls):
        parser = argparse.ArgumentParser(prog='spaced-repetition',
                                         description=CliController.DESCRIPTION)
        sub_parsers = parser.add_subparsers(title='Options')

        # add new problem
        add_parser = sub_parsers.add_parser('add-problem',
                                            aliases=['add', 'ap'],
                                            help='Add new problem')
        add_parser.set_defaults(func=cls._add_problem)

        # list problems
        list_parser = sub_parsers.add_parser('list-problems',
                                             aliases=['l', 'list', 'lp'],
                                             help='List problems in db')
        list_parser.add_argument('-fn', '--filter-name',
                                 help='List only problems whose names contain '
                                      'the provided substring')
        list_parser.add_argument('-ft', '--filter-tags',
                                 nargs='+',
                                 help='List problems with the provided tags')
        list_parser.add_argument('-s', '--sort-by',
                                 choices=['id', 'name'],
                                 nargs=1,
                                 help='Provide space-separated attribute(s) to '
                                      'sort listed problems by')
        list_parser.set_defaults(func=cls._list_problems)

        # add new tag
        add_parser = sub_parsers.add_parser('add-tag',
                                            aliases=['at'],
                                            help='Add new tag')
        add_parser.set_defaults(func=cls._add_tag)

        # list tags
        tag_parser = sub_parsers.add_parser('list-tags',
                                            aliases=['lt', 'tags'],
                                            help='List existing tags')
        tag_parser.add_argument('-f', '--filter',
                                help='List only tags whose tag contains '
                                     'the provided substring')
        tag_parser.set_defaults(func=cls._list_tags)

        # log problem execution
        log_parser = sub_parsers.add_parser('add-log',
                                            aliases=['log', 'al'],
                                            help='List problem logs')
        log_parser.set_defaults(func=cls._add_problem_log)

        return parser.parse_args()

    @classmethod
    def _add_problem(cls, _):
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
        if args.filter_name:
            kwargs['name_substr'] = args.filter_name
        if args.filter_tags:
            kwargs['tags'] = args.filter_tags
        if args.sort_by:
            kwargs['sorted_by'] = args.sort_by
        prob_getter.list_problems(**kwargs)

    @staticmethod
    def _list_tags(args):
        kwargs = {'sort': True}
        if args.filter:
            kwargs['sub_str'] = args.filter

        tags = DjangoGateway.get_tags(**kwargs)
        CliPresenter.list_tags(tags=[t for t in tags])

    @classmethod
    def _add_problem_log(cls, _):
        """Log the execution of a problem"""
        prob_logger = ProblemLogger(db_gateway=DjangoGateway(),
                                    presenter=CliPresenter())
        try:
            problem_name = cls._get_user_input_problem_name()
        except ValueError as err:
            print(err)
            return

        prob_logger.log_problem(
            action=cls._get_user_input_action(),
            problem_id=DjangoGateway.get_problems(name=problem_name)[0].problem_id,
            result=cls._get_user_input_result())

    @staticmethod
    def _get_user_input_action():
        print('\nThe following Action options exist:')
        for a in Action:
            print(f'{a.value}: {a.name}')
        return input('Choose one (int): ')

    @staticmethod
    def _get_user_input_problem_name():
        problem_name = input('Problem name: ')
        if DjangoGateway.problem_exists(name=problem_name):
            return problem_name
        raise ValueError(f'Problem with name {problem_name} does not exist, ',
                         'try searching for similar problems')

    @staticmethod
    def _get_user_input_result():
        print('\nThe following Result options exist:')
        for r in Result:
            print(f'{r.value}: {r.name}')
        return input('Choose one (int): ')

    @classmethod
    def _add_tag(cls, _):
        """Create new Tag"""
        tag_adder = TagAdder(db_gateway=DjangoGateway(),
                             presenter=CliPresenter())
        tag_adder.add_tag(name=input('Tag name: '))


def main():
    CliController.run()


if __name__ == "__main__":
    main()
