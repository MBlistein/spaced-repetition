from typing import List

import pandas as pd
from tabulate import tabulate

from spaced_repetition.domain.problem import Problem
from spaced_repetition.domain.problem_log import ProblemLog
from spaced_repetition.domain.tag import Tag
from spaced_repetition.use_cases.presenter_interface import PresenterInterface
from spaced_repetition.use_cases.helpers import serialize_ts


class CliPresenter(PresenterInterface):
    # ------------------ confirm data creation -----------------------------
    @classmethod
    def confirm_problem_created(cls, problem: Problem):
        print(cls._problem_confirmation_txt(problem=problem))

    @staticmethod
    def _problem_confirmation_txt(problem: Problem):
        return f"Created Problem '{problem.name}' with id " \
               f"'{problem.problem_id}' " \
               f"(difficulty '{problem.difficulty.name}', " \
               f"tags: {', '.join([t.name for t in problem.tags])})"

    @staticmethod
    def confirm_problem_logged(problem: Problem, problem_log: ProblemLog):
        print(f"Logged execution of Problem '{problem.name}' with "
              f"result '{problem_log.result.name}' at "
              f"{serialize_ts(problem_log.timestamp)}.")

    @classmethod
    def confirm_tag_created(cls, tag: Tag) -> None:
        print(cls._tag_confirmation_txt(tag=tag))

    @staticmethod
    def _tag_confirmation_txt(tag: Tag) -> str:
        return f"Created Tag '{tag.name}' with id '{tag.tag_id}'."

    # -------------------- pretty-print db contents ------------------------
    @classmethod
    def list_problems(cls, problems: pd.DataFrame) -> None:
        ordered_cols = ['problem_id', 'problem', 'tags', 'difficulty',
                        'KS', 'RF', 'url']
        formatted_df = cls.format_df(df=problems,
                                     ordered_cols=ordered_cols,
                                     index_col='problem_id')
        tabulated_df = cls.tabulate_df(df=formatted_df)
        print(tabulated_df)

    @classmethod
    def list_problem_tag_combos(cls, problem_tag_combos: pd.DataFrame) -> None:
        ordered_cols = ['tag', 'problem', 'problem_id', 'difficulty', 'last_access',
                        'last_result', 'KS', 'RF', 'url', 'ease', 'interval']
        formatted_df = cls.format_df(df=problem_tag_combos,
                                     ordered_cols=ordered_cols,
                                     index_col='tag')
        tabulated_df = cls.tabulate_df(df=formatted_df)
        print(tabulated_df)

    @classmethod
    def show_problem_history(cls, problem: Problem,
                             problem_log_info: pd.DataFrame) -> None:
        print(f"History for problem '{problem.name}':")
        history_df = problem_log_info \
            .sort_values('ts_logged', ascending=False) \
            .reindex(columns=['ts_logged', 'result', 'comment', 'tags'])

        history_df.result = cls._format_result(history_df.result)
        history_df.ts_logged = cls._format_timestamp(history_df.ts_logged)
        print(cls.tabulate_df(history_df))

    @staticmethod
    def tabulate_df(df: pd.DataFrame):
        return tabulate(df,
                        headers='keys',
                        tablefmt='github')

    @classmethod
    def format_df(cls, df: pd.DataFrame, ordered_cols: List[str],
                  index_col: str):
        """Needs at least a column named 'problem_id'"""
        name_mapper = {'result': 'last_result',
                       'ts_logged': 'last_access'}
        df = df \
            .rename(columns=name_mapper) \
            .reindex(columns=ordered_cols) \
            .set_index(index_col)  # avoid printing some integer index

        df.difficulty = cls._format_difficulty(df.difficulty)
        if 'last_result' in ordered_cols:
            df.last_result = cls._format_result(df.last_result)
        if 'last_access' in ordered_cols:
            df.last_access = cls._format_timestamp(df.last_access)
        return df

    @staticmethod
    def _format_difficulty(difficulty: pd.Series):
        return difficulty.map(lambda x: x.name, na_action='ignore')

    @staticmethod
    def _format_result(result: pd.Series):
        return result.map(lambda x: x.name, na_action='ignore')

    @staticmethod
    def _format_timestamp(ts: pd.Series):
        # if ts consists of only np.NaN, it needs to be cast to datetime
        return pd.to_datetime(ts).dt.strftime('%Y-%m-%d %H:%M')

    @classmethod
    def list_tags(cls, tags: pd.DataFrame) -> None:
        formatted_df = cls.format_tag_df(df=tags)
        tabulated_df = cls.tabulate_df(df=formatted_df)
        print(tabulated_df)

    @staticmethod
    def format_tag_df(df: pd.DataFrame):
        order = ['tag', 'priority', 'KS (weighted avg)', 'experience',
                 'num_problems']

        return df \
            .reindex(columns=order) \
            .set_index('tag')
