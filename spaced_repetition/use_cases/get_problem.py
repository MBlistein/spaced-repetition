from typing import List

from spaced_repetition.domain.problem import (Difficulty,
                                              Problem,
                                              ProblemCreator)
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface


class ProblemGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def list_problems(self):
        self.presenter.list_problems(
            self.repo.get_problems())
