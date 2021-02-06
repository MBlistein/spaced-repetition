from django.db import models

from spaced_repetition.domain.problem import (Difficulty,
                                              MAX_LINK_LENGTH,
                                              MAX_NAME_LENGTH)


class Problem(models.Model):
    DifficultyChoices = models.IntegerChoices(
        value='DifficultyChoices',
        names=[(o.name, o.value) for o in Difficulty])

    # difficulty = models.IntegerField(choices=[(o.name, o.value) for o in Difficulty])
    difficulty = models.IntegerField(choices=DifficultyChoices.choices)
    link = models.CharField(blank=False,
                            max_length=MAX_LINK_LENGTH,
                            null=True)
    name = models.CharField(blank=False,
                            max_length=MAX_NAME_LENGTH,
                            null=False)
    tags = models.JSONField()
