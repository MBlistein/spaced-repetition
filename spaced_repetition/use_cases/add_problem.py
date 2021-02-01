from typing import List

from spaced_repetition.domain.problem import Difficulty, Problem


class ProblemAdder:
    def add_problem(self, name: str,
                    difficulty: Difficulty,
                    tags: List[str],
                    link: str = None):
        problem = Problem(name=name,
                          difficulty=difficulty,
                          tags=tags,
                          link=link)
