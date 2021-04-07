from typing import Union

from spaced_repetition.domain.problem_log import (ProblemLog, ProblemLogCreator,
                                                  Result)
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface


class ProblemLogger:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def log_problem(self, comment: str, problem_name: str, result: Result):
        try:
            problem = self.repo.get_problems(name=problem_name)[0]
        except IndexError:
            raise ValueError(
                f"Problem with name '{problem_name}' does not exist, "
                "try searching for similar problems.")

        last_log = self.get_last_log_for_problem(problem_id=problem.problem_id)

        problem_log = ProblemLogCreator.create(
            comment=comment,
            last_log=last_log,
            problem_id=problem.problem_id,
            result=result)

        self.repo.create_problem_log(problem_log=problem_log)

        self.presenter.confirm_problem_logged(problem=problem,
                                              problem_log=problem_log)

    def get_last_log_for_problem(self, problem_id: int) -> Union[ProblemLog, None]:
        previous_logs = self.repo.get_problem_logs(problem_ids=[problem_id])
        if previous_logs:
            return max(previous_logs, key=lambda p: p.timestamp)
