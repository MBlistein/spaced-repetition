from django.db import models
from django.utils import timezone

from spaced_repetition.domain.problem import (Difficulty,
                                              MAX_URL_LENGTH,
                                              MAX_NAME_LENGTH)
from spaced_repetition.domain.problem_log import (Action,
                                                  Result)


class Problem(models.Model):
    difficulty = models.IntegerField(
        choices=((o.value, o.name) for o in Difficulty))
    name = models.CharField(blank=False,
                            max_length=MAX_NAME_LENGTH,
                            null=False)
    tags = models.JSONField()
    url = models.CharField(blank=False,
                           max_length=MAX_URL_LENGTH,
                           null=True)

    def __str__(self):
        return f"Problem '{self.name}'," \
            f" difficulty '{self.get_difficulty_display()}'," \
            f" tags '{self.tags}', url '{self.url}'"


class ProblemLog(models.Model):
    action = models.IntegerField(choices=((a.value, a.name) for a in Action))
    problem = models.ForeignKey(Problem,
                                on_delete=models.CASCADE,
                                related_name='logs')
    result = models.IntegerField(choices=((r.value, r.name) for r in Result))
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Log: {self.get_action_display()} problem '{self.problem.name}'" \
            f" at {self.timestamp}"
