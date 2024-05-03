"""Модуль для описания представлений и форм блога."""
from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.forms import PostCreateForm, CommentForm, ProfileForm
from blog.models import Post, Comment, Category
from blog.pagination import filter_annotate
from core.mixins import OnlyAuthorMixin
from .cbv_mixins import CommentActionMixin, PostListMixin

User = get_user_model()


class Index(PostListMixin, ListView):
    """Вывод постов на главную страницу."""

    template_name = 'blog/index.html'
    queryset = filter_annotate(Post.objects, filter=True)


class CategoryList(PostListMixin, ListView):
    """Вывод постов по категории."""

    CATEGORY_SLUG_PARAM = 'category_slug'
    template_name = 'blog/category.html'

    def get_category(self):
        if not hasattr(self, '_category'):
            category = get_object_or_404(
                Category,
                slug=self.kwargs[self.CATEGORY_SLUG_PARAM],
                is_published=True
            )
        return category

    def get_queryset(self):
        return filter_annotate(self.get_category().posts, filter=True)

    def get_context_data(self, **kwargs):
        """Добавляем в контекст категорию постов."""
        kwargs['category'] = self.get_category()
        return super().get_context_data(**kwargs)


class ProfileDetailView(SingleObjectMixin, PostListMixin, ListView):
    """Вывод постов на страницу профиля."""

    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=User.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object
        return context

    def get_queryset(self):
        queryset = filter_annotate(
            self.object.posts.all().select_related('category'), annotate=True
        )
        if self.request.user != self.object:
            queryset = filter_annotate(queryset, filter=True)
        return queryset


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    REVERSE_ADRES = 'blog:profile'

    def form_valid(self, form):
        """Подставим значение поля автор из urls."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(self.REVERSE_ADRES,
                       args=(self.request.user.username,))


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'
    GET_SLUG_PARAM = 'post_id'
    REVERSE_ADRES = 'blog:post_detail'

    def form_valid(self, form):
        """Подставляем в форму значения автора и поста."""
        post = get_object_or_404(Post, pk=self.kwargs.get(self.GET_SLUG_PARAM))
        if self.request.user != post.author:
            post = get_object_or_404(
                filter_annotate(Post.objects.filter(pk=post.pk), filter=True)
            )
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Переадресация."""
        return reverse(self.REVERSE_ADRES,
                       args=(self.kwargs.get(self.GET_SLUG_PARAM),))


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class CommentUpdateView(OnlyAuthorMixin, CommentActionMixin, UpdateView):
    """Редактирование комментария."""

    form_class = CommentForm


class PostDetailView(DetailView):
    """Просмотр поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        queryset = self.get_queryset()
        post = super().get_object()
        if self.request.user != post.author:
            return super().get_object(filter_annotate(queryset,
                                                      filter=True,
                                                      annotate=False))
        return post

    def get_context_data(self, **kwargs):
        """Добавляем форму и оптимизируем запрос."""
        context = super().get_context_data(
            comments=self.object.comments.select_related('author'),
            **kwargs)
        if self.request.user.is_authenticated:
            context['form'] = CommentForm()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""

    form_class = ProfileForm
    model = User
    template_name = 'blog/user.html'
    REVERSE_ADRES = 'blog:profile'

    def get_success_url(self):
        """Получение URL для перенаправления при успешной валидации формы."""
        return reverse(self.REVERSE_ADRES,
                       args=(self.request.user.username,))

    def get_object(self):
        return self.request.user


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление поста."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    REVERSE_ADRES = 'blog:profile'

    def get_success_url(self):
        return reverse(self.REVERSE_ADRES,
                       args=(self.request.user.username,))

    def get_context_data(self, **kwargs):
        """Добавляет в контекст сведения о форме."""
        context = super().get_context_data(**kwargs)
        context['form'] = PostCreateForm(instance=get_object_or_404(
            Post,
            pk=self.kwargs.get(self.pk_url_kwarg)
        ))
        return context


class CommentDeleteView(OnlyAuthorMixin, CommentActionMixin, DeleteView):
    """Удаление комментария."""

    def get_context_data(self, **kwargs):
        """Получить контекст данных."""
        return super().get_context_data(deleting=True, **kwargs)
