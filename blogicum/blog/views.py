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

COUNT_PAGINATE = 10


class CommentActionMixin:
    """Миксин для действий с комментариями."""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
    GET_SLUG_PARAM = 'post_id'
    REVERSE_ADRES = 'blog:post_detail'

    def get_success_url(self):
        """Получить URL для переадресации."""
        return reverse(self.REVERSE_ADRES,
                       args=[self.kwargs.get(self.GET_SLUG_PARAM)])


class PostListMixin:
    """Миксин для действий с комментариями."""

    model = Post
    paginate_by = COUNT_PAGINATE


class CategoryList(PostListMixin, ListView):
    """Вывод постов по категории."""

    CATEGORY_SLUG_PARAM = 'category_slug'
    template_name = 'blog/category.html'

    def get_category(self):
        if not hasattr(self, '_category'):
            self._category = get_object_or_404(
                Category,
                slug=self.kwargs[self.CATEGORY_SLUG_PARAM],
                is_published=True
            )
        return self._category

    def get_queryset(self):
        category = self.get_category()
        return filter_annotate(category.posts, filter=True)

    def get_context_data(self, **kwargs):
        """Добавляем в контекст категорию постов."""
        kwargs['category'] = self.get_category()
        return super().get_context_data(**kwargs)


class Index(PostListMixin, ListView):
    """Вывод постов на главную страницу."""

    template_name = 'blog/index.html'
    queryset = filter_annotate(Post.objects, filter=True)


class ProfileDetailView(PostListMixin, ListView):
    """Вывод постов на страницу профиля."""

    template_name = 'blog/profile.html'
    PROFILE_SLUG_PARAM = 'username'

    def get_author(self):
        return get_object_or_404(get_user_model(),
                                 username=self.kwargs[self.PROFILE_SLUG_PARAM])

    def get_queryset(self):
        """Выбор постов по автору, добавляем кол-во комментариев."""
        if self.get_author() != self.request.user:
            return filter_annotate(Post.objects, filter=True)
        return filter_annotate(self.get_author().posts.all())

    def get_context_data(self, **kwargs):
        """Добавляем в контекст данные профиля."""
        return super().get_context_data(profile=self.get_author(), **kwargs)


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

    def get_object(self, queryset=None):
        queryset = self.get_queryset()
        post = super().get_object(queryset=queryset)
        if self.request.user == post.author:
            return get_object_or_404(
                queryset,
                pk=self.kwargs.get(self.pk_url_kwarg)
            )
        return get_object_or_404(
            filter_annotate(queryset, filter=True, annotate=False),
            pk=self.kwargs.get(self.pk_url_kwarg),
        )

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
    model = get_user_model()
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
