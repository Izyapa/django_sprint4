"""Модуль для описания форм."""
from django import forms  # type: ignore
from django.contrib.auth.forms import UserChangeForm  # type: ignore
from django.contrib.auth.models import User  # type: ignore

from .models import Post, Comment


class PostCreateForm(forms.ModelForm):
    """Форма поста."""

    class Meta:
        """Класс мета."""

        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
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
