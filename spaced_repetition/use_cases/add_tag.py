"""UseCase: Create new Tag"""

from spaced_repetition.domain.tag import Tag, TagCreator
from spaced_repetition.use_cases.db_gateway_interface import DBGatewayInterface
from spaced_repetition.use_cases.presenter_interface import PresenterInterface


class TagAdder:
    def __init__(self, db_gateway: DBGatewayInterface,
                 presenter: PresenterInterface):
        self.repo = db_gateway
        self.presenter = presenter

    def add_tag(self, name: str):
        tag = TagCreator.create_tag(name=name)

        self._assert_is_unique(tag=tag)
        new_tag = self.repo.create_tag(tag=tag)
        self.presenter.confirm_tag_created(tag=new_tag)

    def _assert_is_unique(self, tag: Tag):
        if self.repo.tag_exists(name=tag.name):
            raise ValueError(f"Tag with name '{tag.name}' already exists!")
