import uuid

from django.db import models


class TaskManager(models.Manager):

    def save_task_params(self, title_types, release_date, genres, user_rating, countries):
        task_params = self.model(
            title_types=title_types,
            release_date=release_date,
            genres=genres,
            user_rating=user_rating,
            countries=countries,
        )
        task_params.save(using=self.db)

        return task_params


class Task(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title_types = models.CharField(max_length=255, blank=False, default='Feature Film')
    release_date = models.CharField(max_length=255, blank=False, default='2019-01-01,2020-01-01')
    start_release_date = models.CharField(max_length=255, blank=False, default='2019-01-01')
    end_release_date = models.CharField(max_length=255, blank=False, default='2020-01-01')
    genres = models.CharField(max_length=255, blank=False, default='comedy')
    user_rating = models.CharField(max_length=255, blank=False, default='1.0,9.9')
    lower_user_rating = models.CharField(max_length=255, blank=False, default='1.0')
    upper_user_rating = models.CharField(max_length=255, blank=False, default='9.9')
    countries = models.CharField(max_length=255, blank=False, default='cn,us')
    link = models.TextField(blank=True)
    status = models.CharField(max_length=255, blank=False, default='In progress')  # TODO: Use ENUM approach
    result_json = models.JSONField(blank=True, default=dict)

    objects = TaskManager()
