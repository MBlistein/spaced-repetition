from enum import Enum

from spaced_repetition.domain.problem_log import Result


class Score(Enum):
    VERY_GOOD = 5
    GOOD = 4
    MEDIUM = 3
    POOR = 2
    BAD = 1


SCORE_MAPPER = {
    Result.SOLVED_OPTIMALLY_IN_UNDER_25.value: Score.VERY_GOOD,
    Result.SOLVED_OPTIMALLY_SLOWER.value: Score.MEDIUM,
    Result.SOLVED_OPTIMALLY_WITH_HINT.value: Score.MEDIUM,
    Result.SOLVED_SUBOPTIMALLY_IN_UNDER_25.value: Score.MEDIUM,
    Result.SOLVED_SUBOPTIMALLY_SLOWER.value: Score.POOR,
    Result.SOLVED_SUBOPTIMALLY_WITH_HINT.value: Score.POOR,
    Result.NO_IDEA.value: Score.BAD
}
