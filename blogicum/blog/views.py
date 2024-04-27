"""Модуль для описания представлений и форм блога."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse
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


class ProfileDetailView(PostListMixin, ListView):
    """Вывод постов на страницу профиля."""

    template_name = 'blog/profile.html'
    PROFILE_SLUG_PARAM = 'username'

    def get_author(self):
        return get_object_or_404(User,
                                 username=self.kwargs[self.PROFILE_SLUG_PARAM])

    def get_queryset(self):
        """Выбор постов по автору, добавляем кол-во комментариев."""
        author = self.get_author()
        if author != self.request.user:
            return filter_annotate(author.posts.all(), filter=True)
        return filter_annotate(author.posts.all())

    def get_context_data(self, **kwargs):
        """Добавляем в контекст данные профиля."""
        kwargs['profile'] = self.get_author()
        return super().get_context_data(**kwargs)


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
            form.instance.post = post
            form.instance.author = self.request.user
            return super().form_valid(form)

    def get_success_url(self):
        """Переадресация."""
        return reverse(self.REVERSE_ADRES,
                       args=[self.kwargs.get(self.GET_SLUG_PARAM)])


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
        return super().get_context_data(
            form=CommentForm(),
            comments=self.object.comments.select_related('author'),
            **kwargs
        )


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

    def get_context_data(self, **kwargs):
        """Добавление формы с instance в контекст."""
        return super().get_context_data(
            form=PostCreateForm(
                instance=get_object_or_404(
                    Post,
                    author=self.request.user)), **kwargs)

    def get_success_url(self):
        """Переадресация."""
        return reverse(self.REVERSE_ADRES,
                       kwargs={'username': self.request.user.username})


class CommentDeleteView(OnlyAuthorMixin, CommentActionMixin, DeleteView):
    """Удаление комментария."""

    def get_context_data(self, **kwargs):
        """Получить контекст данных."""
        return super().get_context_data(deleting=True, **kwargs)
