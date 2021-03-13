from typing import List

import pandas as pd
from tabulate import tabulate

from spaced_repetition.domain.problem import Problem
from spaced_repetition.domain.tag import Tag, MAX_TAG_LENGTH
from spaced_repetition.use_cases.presenter_interface import PresenterInterface


class CliPresenter(PresenterInterface):
    @classmethod
    def confirm_problem_created(cls, problem: Problem):
        print(cls._problem_confirmation_txt(problem=problem))

    @staticmethod
    def _problem_confirmation_txt(problem: Problem):
        return f"Created Problem '{problem.name}' with id " \
               f"'{problem.problem_id}' (difficulty '" \
               f"{problem.difficulty.name}', tags: {', '.join(problem.tags)})"

    @classmethod
    def list_problems(cls, problems: pd.DataFrame) -> None:
        formatted_df = cls.format_problem_df(df=problems)
        tabluated_df = cls.tabulate_df(df=formatted_df)
        print(tabluated_df)

    @staticmethod
    def tabulate_df(df: pd.DataFrame):
        return tabulate(df,
                        headers='keys',
                        tablefmt='github')

    @staticmethod
    def format_problem_df(df: pd.DataFrame):
        """Needs at least a column named 'problem_id'"""
        existing_columns = df.columns
        name_mapper = {'problem_id': 'id'}
        order = ['name', 'tags', 'difficulty', 'score', 'rank', 'url']

        return df \
            .rename(columns=name_mapper) \
            .set_index('id') \
            .reindex(columns=[col for col in order if col in existing_columns])

    @classmethod
    def list_tags(cls, tags: List[Tag]) -> None:
        num_cols = 2
        column_widths = [5, MAX_TAG_LENGTH]
        print('\nTags:')
        print(cls._format_table_row(content=['Id', 'Tag'],
                                    column_widths=column_widths,
                                    num_cols=num_cols))

        for t in tags:
            print(cls._format_table_row(content=[str(t.tag_id), t.name],
                                        column_widths=column_widths,
                                        num_cols=num_cols))

    @staticmethod
    def _format_entry(entry: str, max_len: int):
        return entry[:max_len].ljust(max_len)

    @classmethod
    def _format_table_row(cls, content: List[str], column_widths: List[int],
                          num_cols: int) -> str:
        if len(content) != num_cols:
            raise ValueError(f'Need exactly {num_cols} entries!')

        row_content = []
        for idx, entry in enumerate(content):
            row_content.append(cls._format_entry(entry=entry,
                                                 max_len=column_widths[idx]))

        return '| ' + ' | '.join(row_content) + ' |'

    @classmethod
    def confirm_tag_created(cls, tag: Tag) -> None:
        print(cls._tag_confirmation_txt(tag=tag))

    @staticmethod
    def _tag_confirmation_txt(tag: Tag) -> str:
        return f"Created Tag '{tag.name}' with id '{tag.tag_id}'."
