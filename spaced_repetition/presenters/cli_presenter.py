from typing import List

from spaced_repetition.domain.problem import Problem
from spaced_repetition.use_cases.presenter_interface import PresenterInterface


NUM_COLUMNS = 5
COLUMN_WIDTHS = [5, 20, 20, 10, 25]


class CliPresenter(PresenterInterface):
    @classmethod
    def confirm_problem_created(cls, problem: Problem):
        print(cls._problem_confirmation_txt(problem=problem))

    @classmethod
    def list_problems(cls, problems: List[Problem]) -> None:
        print('\nProblems:')
        print(cls._format_table_row(
            content=['Id', 'Name', 'Tags', 'Difficulty', 'URL']))

        for p in problems:
            print(cls._format_table_row(content=[
                str(p.problem_id), p.name, ', '.join(p.tags),
                str(p.difficulty.name), p.url]))

    @staticmethod
    def _format_entry(entry: str, max_len: int):
        return entry[:max_len].ljust(max_len)

    @classmethod
    def _format_table_row(cls, content: List[str]) -> str:
        if len(content) != NUM_COLUMNS:
            raise ValueError(f'Need exactly {NUM_COLUMNS} entries!')

        row_content = []
        for idx, entry in enumerate(content):
            row_content.append(cls._format_entry(entry=entry,
                                                 max_len=COLUMN_WIDTHS[idx]))

        return '| ' + ' | '.join(row_content) + ' |'

    @staticmethod
    def _problem_confirmation_txt(problem: Problem):
        return f"Created Problem '{problem.name}' with id '{problem.problem_id}'" \
            f" (difficulty '{problem.difficulty.name}', tags: {', '.join(problem.tags)})"
