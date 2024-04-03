from django import forms
from .models import Post, Comment
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User


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


class CustomProfileForm(UserChangeForm):
    """Форма пользователя."""

    class Meta:
        """Класс мета."""

        model = User
        fields = ('first_name',
                  'last_name',
                  'username',
                  'email')
