from enum import Enum, unique

from spaced_repetition.domain.problem_log import Result


@unique
class Score(Enum):
    VERY_GOOD = 4
    GOOD = 3
    MEDIUM = 2
    POOR = 1
    BAD = 0


SCORE_MAPPER = {
    Result.KNEW_BY_HEART.value: Score.VERY_GOOD,
    Result.SOLVED_OPTIMALLY_IN_UNDER_25.value: Score.GOOD,
    Result.SOLVED_OPTIMALLY_SLOWER.value: Score.MEDIUM,
    Result.SOLVED_OPTIMALLY_WITH_HINT.value: Score.POOR,
    Result.SOLVED_SUBOPTIMALLY.value: Score.POOR,
    Result.NO_IDEA.value: Score.BAD
}
