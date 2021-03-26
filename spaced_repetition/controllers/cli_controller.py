"""Command line controller / user interface"""

import argparse

from spaced_repetition.domain.problem import Difficulty
from spaced_repetition.domain.problem_log import Result
from spaced_repetition.gateways.django_gateway.django_gateway import DjangoGateway
from spaced_repetition.presenters.cli_presenter import CliPresenter
from spaced_repetition.use_cases.add_problem import ProblemAdder
from spaced_repetition.use_cases.add_tag import TagAdder
from spaced_repetition.use_cases.get_problem import ProblemGetter
from spaced_repetition.use_cases.get_tag import TagGetter
from spaced_repetition.use_cases.log_problem import ProblemLogger


class CliController:
    DESCRIPTION = """This is the spaced-repetition CLI"""

    @classmethod
    def run(cls):
        args = cls._parse_args()
        args.func(args)

    @classmethod
    def _parse_args(cls):
        # TODO: install this program to be called from the command line via
        #  'spaced-repetition'
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
        list_parser.add_argument(
            '-ftl', '--filter-tags-all',
            nargs='+',
            help='List problems containing all provided tags')
        list_parser.add_argument(
            '-fty', '--filter-tags-any',
            nargs='+',
            help='List problems containing any of the provided tags')
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
                                            help='Add new problem log')
        log_parser.set_defaults(func=cls._add_problem_log)

        return parser.parse_args()

    # -------------------- add problem --------------------
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

    @staticmethod
    def _format_difficulty(difficulty: str):
        return Difficulty(int(difficulty))

    @staticmethod
    def _format_tags(tags: str):
        return tags.split()

    # -------------------- log problem --------------------
    @classmethod
    def _add_problem_log(cls, _):
        """Log the execution of a problem"""
        problem_name = cls._get_problem_name()
        try:
            result = cls._get_user_input_result()
        except ValueError as err:
            print(f"\nSupplied invalid Result!\n{err}")
            return

        prob_logger = ProblemLogger(db_gateway=DjangoGateway(),
                                    presenter=CliPresenter())
        try:
            prob_logger.log_problem(problem_name=problem_name,
                                    result=result)
        except ValueError as err:
            print(err)

    # -------------------- add tag --------------------

    @classmethod
    def _add_tag(cls, _):
        """Create new Tag"""
        tag_adder = TagAdder(db_gateway=DjangoGateway(),
                             presenter=CliPresenter())
        tag_adder.add_tag(name=cls._clean_input(input('Tag name: ')))

    # -------------------- get user input --------------------

    @classmethod
    def _get_problem_name(cls):
        return cls._clean_input(input("Problem name: "))

    @classmethod
    def _get_user_input_result(cls) -> Result:
        print('\nThe following Result options exist:')
        for r in Result:
            print(f'{r.value}: {r.name}')

        user_choice = cls._clean_input(input('Choose one (int): '))
        return Result(int(user_choice))

    @staticmethod
    def _clean_input(user_input: str) -> str:
        return user_input.strip()

    @classmethod
    def _record_problem_data(cls) -> dict:
        sorted_difficulties = list(sorted([diff for diff in Difficulty],
                                          key=lambda d: d.value))
        min_diff, max_diff = sorted_difficulties[0], sorted_difficulties[-1]
        return {
            'name': cls._get_problem_name(),
            'difficulty': cls._format_difficulty(
                cls._clean_input(
                    input(f"Choose a difficulty between "
                          f"{min_diff.value} ({min_diff.name}) and "
                          f"{max_diff.value} ({max_diff.name}): "))),
            'url': cls._clean_input(input("Url (optional): ")),
            'tags': cls._format_tags(
                input("Supply whitespace-separated tags (at least one): "))}

    # -------------------- display elements --------------------
    @staticmethod
    def _list_problems(args):
        prob_getter = ProblemGetter(db_gateway=DjangoGateway(),
                                    presenter=CliPresenter())
        kwargs = {}
        if args.filter_name:
            kwargs['name_substr'] = args.filter_name
        if args.filter_tags_all:
            kwargs['tags_all'] = args.filter_tags_all
        if args.filter_tags_any:
            kwargs['tags_any'] = args.filter_tags_any
        if args.sort_by:
            kwargs['sorted_by'] = args.sort_by
        prob_getter.list_problems(**kwargs)

    @staticmethod
    def _list_tags(args):
        kwargs = {}
        if args.filter:
            kwargs['sub_str'] = args.filter

        tag_getter = TagGetter(db_gateway=DjangoGateway(),
                               presenter=CliPresenter())
        tag_getter.list_tags(**kwargs)


def main():
    CliController.run()


if __name__ == "__main__":
    main()
