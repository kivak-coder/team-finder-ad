from django import forms
from core.mixins import GitHubURLMixin

from .models import Project


class ProjectForm(GitHubURLMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'github_url', 'status')
