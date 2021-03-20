import pandas as pd
from tabulate import tabulate

from spaced_repetition.domain.problem import Problem
from spaced_repetition.domain.tag import Tag
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
    def confirm_tag_created(cls, tag: Tag) -> None:
        print(cls._tag_confirmation_txt(tag=tag))

    @staticmethod
    def _tag_confirmation_txt(tag: Tag) -> str:
        return f"Created Tag '{tag.name}' with id '{tag.tag_id}'."

    @classmethod
    def list_problems(cls, problems: pd.DataFrame) -> None:
        # TODO: deal with empty problem df
        formatted_df = cls.format_problem_df(df=problems)
        tabulated_df = cls.tabulate_df(df=formatted_df)
        print(tabulated_df)

    @staticmethod
    def tabulate_df(df: pd.DataFrame):
        return tabulate(df,
                        headers='keys',
                        tablefmt='github')

    @staticmethod
    def format_problem_df(df: pd.DataFrame):
        """Needs at least a column named 'problem_id'"""
        name_mapper = {'problem_id': 'id',
                       'ts_logged': 'last_access'}
        df = df \
            .rename(columns=name_mapper) \
            .set_index('id') \

        df.last_access = df.last_access.dt.strftime('%Y-%m-%d %H:%M')

        existing_columns = df.columns
        order = ['name', 'tags', 'difficulty', 'last_access',
                 'rank', 'url']

        return df \
            .reindex(columns=[col for col in order if col in existing_columns])

    @classmethod
    def list_tags(cls, tags: pd.DataFrame) -> None:
        formatted_df = cls.format_tag_df(df=tags)
        tabulated_df = cls.tabulate_df(df=formatted_df)
        print(tabulated_df)

    @staticmethod
    def format_tag_df(df: pd.DataFrame):
        """Needs at least a column named 'problem_id'"""
        # TODO: deal with empty problem df
        df.last_access = df.last_access.dt.strftime('%Y-%m-%d %H:%M')

        existing_columns = df.columns
        order = ['prio', 'tags', 'avg_score', 'last_access', 'num_problems']

        return df \
            .reindex(columns=[col for col in order if col in existing_columns])
