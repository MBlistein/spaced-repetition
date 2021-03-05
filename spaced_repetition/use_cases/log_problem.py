import datetime as dt

from spaced_repetition.domain.problem_log import Action, ProblemLog, Result
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface


class ProblemLogger:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def log_problem(self,
                    action: Action,
                    problem_id: int,
                    result: Result,
                    timestamp: dt.datetime = None):
        self.repo.create_problem_log(problem_log=ProblemLog(
            action=action,
            problem_id=problem_id,
            result=result,
            timestamp=timestamp))
