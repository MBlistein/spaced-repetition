from typing import List

from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface


class ProblemGetter:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def list_problems(self, name_substr: str = None,
                      sorted_by: List[str] = None):
        self.presenter.list_problems(
            self.repo.get_problems(sorted_by=sorted_by or None,
                                   name_substr=name_substr))
