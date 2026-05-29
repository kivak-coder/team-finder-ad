from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from core.mixins import GitHubURLMixin
from .models import User


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('name', 'surname', 'email', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')


class ProfileEditForm(GitHubURLMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'surname', 'avatar', 'about', 'phone', 'github_url')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            return phone

        digits = ''.join([c for c in phone if c.isdigit()])
        if len(digits) != 11:
            raise ValidationError("Номер должен содержать 11 цифр.")

        if digits[0] == '8':
            digits = '7' + digits[1:]
        elif digits[0] != '7':
            raise ValidationError("Номер должен начинаться с 8 или +7.")

        final_phone = f"+{digits}"

        qs = User.objects.filter(phone=final_phone)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("Этот номер уже занят.")

        return final_phone


class ChangePasswordForm(PasswordChangeForm):
    pass
