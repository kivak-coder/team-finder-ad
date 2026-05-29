from django.conf import settings
from django.db import models
from django.urls import reverse

from team_finder.constants import (
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_MAX_LENGTH,
    PROJECT_STATUS_OPEN,
)


class Project(models.Model):
    STATUS_CHOICES = [
        (PROJECT_STATUS_OPEN, "Open"),
        (PROJECT_STATUS_CLOSED, "Closed"),
    ]

    name = models.CharField(max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='participated_projects',
        blank=True
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.pk})
