"""Модуль для описания представлений и форм блога."""
from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.views.generic.edit import FormView

from blog.forms import PostCreateForm, CommentForm, ProfileForm
from blog.models import Post, Comment, Category
from blog.utils import (
    annotate_comments_and_order, filter_published_date_annotate_comments)
from core.mixins import OnlyAuthorMixin

COUNT_PAGINATE = 10


class CategoryList(ListView):
    """Вывод постов по категории."""

    template_name = 'blog/category.html'
    model = Post
    paginate_by = COUNT_PAGINATE

    def get_category(self):
        return get_object_or_404(Category,
                                 slug=self.kwargs['category_slug'],
                                 is_published=True)

    def get_queryset(self):
        return filter_published_date_annotate_comments(
            self.get_category().posts
            )

    def get_context_data(self, **kwargs):
        """Добавляем в контекст категорию постов."""
        return super().get_context_data(category=self.get_category(), **kwargs)


class Index(ListView):
    """Вывод постов на главную страницу."""

    template_name = 'blog/index.html'
    model = Post
    paginate_by = COUNT_PAGINATE
    queryset = filter_published_date_annotate_comments(Post.objects)


class ProfileDetailView(ListView):
    """Вывод постов на страницу профиля."""

    template_name = 'blog/profile.html'
    model = Post
    paginate_by = COUNT_PAGINATE

    def get_author(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        """Выбор постов по автору, добавляем кол-во комментариев."""
        if self.get_author() == self.request.user:
            return annotate_comments_and_order(self.get_author().posts.all())
        return filter_published_date_annotate_comments(Post.objects)

    def get_context_data(self, **kwargs):
        """Добавляем в контекст данные профиля."""
        return super().get_context_data(profile=self.get_author(), **kwargs)


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Подставим значение поля автор из urls."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       args=[self.request.user.username])


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        """Подставляем в форму значения автора и поста."""
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:post_detail',
                       args=[self.kwargs.get('post_id')])


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:post_detail',
                       args=[self.kwargs.get('post_id')])


class PostDetailView(DetailView):
    """Просмотр поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        obj = super().get_object(queryset=queryset)
        if self.request.user == obj.author:
            return get_object_or_404(
                queryset,
                pk=self.kwargs.get(self.pk_url_kwarg)
            )
        return get_object_or_404(
                queryset,
                pk=self.kwargs.get(self.pk_url_kwarg),
                is_published=True,
                category__is_published=True
            )

    def get_context_data(self, **kwargs):
        """Добавляем форму и оптимизируем запрос."""
        return super().get_context_data(
            form=CommentForm(),
            comments=self.object.comments.select_related('author'),
            **kwargs
            )


class ProfileUpdateView(LoginRequiredMixin, FormView):
    """Редактирование профиля."""

    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        """Получение URL для перенаправления при успешной валидации формы."""
        return reverse('blog:profile',
                       args=[self.request.user.username])

    def form_valid(self, form):
        """Сохранение формы и перенаправление на страницу профиля."""
        form.save()
        return redirect(self.get_success_url())

    def get_form_kwargs(self):
        """Получение аргументов для инициализации формы."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        return super().get_context_data(profile=self.request.user, **kwargs)


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление поста."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        """Добавление формы с instance в контекст."""
        form = PostCreateForm(
            instance=get_object_or_404(Post,
                                       author=self.request.user))
        return super().get_context_data(form=form, **kwargs)

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    template_name = 'blog/comment.html'
    context_object_name = 'comment'
    pk_url_kwarg = 'comment_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deleting'] = True
        return context

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=[self.kwargs.get('post_id')])
