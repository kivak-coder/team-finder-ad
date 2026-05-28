import random
from io import BytesIO
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
import os

class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        if not user.avatar:
            user.generate_default_avatar()
        return user

    def create_superuser(self, email, name, surname, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, name, surname, phone, password, **extra_fields)

class Skill(models.Model):
    name = models.CharField(max_length=124, unique=True)

    def __str__(self):
        return self.name

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=12)
    github_url = models.URLField(blank=True, null=True)
    about = models.TextField(max_length=256, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    favorites = models.ManyToManyField('Project', related_name='interested_users', blank=True)
    skills = models.ManyToManyField(Skill, related_name='users', blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'phone']

    def __str__(self):
        return f"{self.name} {self.surname}"

    def generate_default_avatar(self):
        """Generate a simple 200x200 avatar with first letter on pastel background."""
        colors = [
            '#FFB3BA', '#C5E0B4', '#FFD4A8', '#B5E3FF', '#E0BBE4', '#B0E57C',
            '#FDD0F9', '#9ED9CC', '#FFCC99', '#C9E4DE'
        ]
        bg_color = random.choice(colors)
        text = self.name[0].upper() if self.name else '?'
        img = Image.new('RGB', (200, 200), color=bg_color)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 100)
        except:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0,0), text, font=font)
        w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text(((200-w)/2, (200-h)/2), text, fill='#4A4A4A', font=font)
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f"avatar_{self.email.split('@')[0]}.png"
        self.avatar.save(filename, ContentFile(buffer.getvalue()), save=False)
        buffer.close()

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            super().save(*args, **kwargs)
            self.generate_default_avatar()
        super().save(*args, **kwargs)

class Project(models.Model):
    STATUS_CHOICES = [('open', 'Open'), ('closed', 'Closed')]
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default='open')
    participants = models.ManyToManyField(User, related_name='participated_projects', blank=True)

    def __str__(self):
        return self.name