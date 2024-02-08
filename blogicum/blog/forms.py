from django import forms
from .models import Post, Comment
# Импортируем функцию-валидатор.
from django.core.exceptions import ValidationError


class BlogCreateForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        return text.split()[0]


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
