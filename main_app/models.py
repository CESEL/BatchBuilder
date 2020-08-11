from django.db import models


class Build(models.Model):
    repo_id = models.IntegerField()
    head_commit = models.CharField(max_length=40)
    is_merged = models.BooleanField(default=False)

