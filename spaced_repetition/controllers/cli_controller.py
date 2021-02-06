"""Command line controller / user interface"""

from spaced_repetition.gateways.django_gateway.django_gateway import DjangoGateway
from spaced_repetition.use_cases.add_problem import ProblemAdder


def get_input() -> dict:
    return {
        'name': input("Problem name: "),
        'difficulty': int(input("Select a difficulty from 1 (easy) to 3 (hard): ")),
        'link': input("Link (optional): "),
        'tags': input("Supply whitespace-separated tags (at least one): ")}


def main():
    prob_adder = ProblemAdder(db_gateway=DjangoGateway())
    user_input = get_input()
    try:
        prob_adder.add_problem(
            difficulty=user_input['difficulty'],
            link=user_input['link'],
            name=user_input['name'],
            tags=user_input['tags'])
    except ValueError as err:
        print(err)
        return


if __name__ == "__main__":
    main()
