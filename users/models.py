from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from django.urls import reverse

from .managers import UserManager
from team_finder.constants import (
    USER_NAME_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH,
)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(max_length=USER_SURNAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True
    )
    github_url = models.URLField(blank=True, null=True)
    about = models.TextField(max_length=USER_ABOUT_MAX_LENGTH,
                             blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    favorites = models.ManyToManyField(
        'projects.Project',
        related_name='interested_users',
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        from .services import generate_avatar
        if not self.avatar:
            self.avatar = generate_avatar(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('users:user_detail', kwargs={'pk': self.pk})
