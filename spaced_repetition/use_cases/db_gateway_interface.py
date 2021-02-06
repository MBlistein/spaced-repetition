from spaced_repetition.domain.problem import Problem


class DBGatewayInterface:
    @staticmethod
    def create_problem(problem: Problem) -> None:
        pass
