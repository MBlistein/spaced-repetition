from django.db import models

from spaced_repetition.domain.problem import (Difficulty,
                                              MAX_NAME_LENGTH,
                                              MAX_URL_LENGTH)
from spaced_repetition.domain.problem_log import Result
from spaced_repetition.domain.tag import MAX_TAG_LENGTH


class Tag(models.Model):
    experience_target = models.IntegerField(
        blank=False,
        null=False
    )

    name = models.CharField(
        blank=False,
        max_length=MAX_TAG_LENGTH,
        null=False)

    def __str__(self):
        return self.name


class Problem(models.Model):
    difficulty = models.IntegerField(
        choices=((o.value, o.name) for o in Difficulty))
    name = models.CharField(blank=False,
                            max_length=MAX_NAME_LENGTH,
                            null=False)
    tags = models.ManyToManyField(Tag,
                                  related_name='problems')
    url = models.CharField(blank=True,
                           max_length=MAX_URL_LENGTH,
                           null=False)

    def __str__(self):
        return f"Problem '{self.name}'," \
            f" difficulty '{self.get_difficulty_display()}', url '{self.url}'"


class ProblemLog(models.Model):
    comment = models.CharField(max_length=255, blank=True, null=False)
    problem = models.ForeignKey(Problem,
                                on_delete=models.CASCADE,
                                related_name='logs')
    result = models.IntegerField(choices=((r.value, r.name) for r in Result))
    tags = models.ManyToManyField(Tag,
                                  related_name='problem_logs')
    timestamp = models.DateTimeField(null=False)

    def __str__(self):
        return f"Problem '{self.problem.name}' attempted at {self.timestamp} " \
            f"with result {self.result} and tags " \
            f"{[t.name for t in self.tags.all()]}."
