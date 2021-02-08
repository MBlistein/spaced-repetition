from spaced_repetition.use_cases.presenter_interface import PresenterInterface

from spaced_repetition.domain.problem import Problem


class CliPresenter(PresenterInterface):
    @classmethod
    def confirm_problem_created(cls, problem: Problem):
        print(cls._problem_confirmation_txt(problem=problem))

    @staticmethod
    def _problem_confirmation_txt(problem: Problem):
        return f"Created Problem '{problem.name}' (difficulty " \
               f"'{problem.difficulty.name}', tags: {', '.join(problem.tags)})"
