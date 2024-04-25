"""Модуль для описания форм."""
from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

from .models import Post, Comment


class PostCreateForm(forms.ModelForm):
    """Форма поста."""

    class Meta:
        """Класс мета."""

        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):
    """Форма комментария."""

    class Meta:
        """Класс мета."""

        model = Comment
        fields = ('text',)


class ProfileForm(UserChangeForm):
    """Форма пользователя."""

    class Meta:
        """Класс мета."""

        model = User
        fields = ('first_name',
                  'last_name',
                  'username',
                  'email')
