"""Command line controller / user interface"""

from spaced_repetition.gateways.django_gateway.django_gateway import DjangoGateway
from spaced_repetition.use_cases.add_problem import ProblemAdder
from spaced_repetition.domain.problem import Difficulty


class CliController:
    @classmethod
    def _get_input(cls) -> dict:
        sorted_diffs = list(sorted([diff for diff in Difficulty],
                                   key=lambda d: d.value))
        min_diff = sorted_diffs[0]
        max_diff = sorted_diffs[-1]
        return {
            'name': input("Problem name: "),
            'difficulty': cls._format_difficulty(
                input(f"Select a difficulty from {min_diff.value} ({min_diff.name})"
                      f" to {max_diff.value} ({max_diff.name}): ")),
            'link': input("Link (optional): "),
            'tags': cls._format_tags(
                input("Supply whitespace-separated tags (at least one): "))}

    @staticmethod
    def _format_difficulty(difficulty: str):
        return Difficulty(int(difficulty))

    @staticmethod
    def _format_tags(tags: str):
        return tags.split()

    @classmethod
    def run(cls):
        prob_adder = ProblemAdder(db_gateway=DjangoGateway())
        user_input = cls._get_input()
        try:
            prob_adder.add_problem(
                difficulty=user_input['difficulty'],
                link=user_input['link'],
                name=user_input['name'],
                tags=user_input['tags'])
        except ValueError as err:
            print(err)
            return


def main():
    cli = CliController
    cli.run()


if __name__ == "__main__":
    main()
