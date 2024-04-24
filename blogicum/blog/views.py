"""Модуль для описания представлений и форм блога."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from blog.forms import PostCreateForm, CommentForm, ProfileForm
from blog.models import Post, Comment, Category
from blog.utils import filter_annotate
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
        return filter_annotate(
            self.get_category().posts, filter=True
        )

    def get_context_data(self, **kwargs):
        """Добавляем в контекст категорию постов."""
        return super().get_context_data(category=self.get_category(), **kwargs)


class Index(ListView):
    """Вывод постов на главную страницу."""

    template_name = 'blog/index.html'
    model = Post
    paginate_by = COUNT_PAGINATE
    queryset = filter_annotate(Post.objects, filter=True)


class ProfileDetailView(ListView):
    """Вывод постов на страницу профиля."""

    template_name = 'blog/profile.html'
    model = Post
    paginate_by = COUNT_PAGINATE

    def get_author(self):
        return get_object_or_404(User, username=self.kwargs['username'])

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
        post = super().get_object(queryset=self.get_queryset())
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
    model = User
    template_name = 'blog/user.html'

    def get_success_url(self):
        """Получение URL для перенаправления при успешной валидации формы."""
        return reverse('blog:profile',
                       args=[self.request.user.username])

    def get_object(self):
        return self.request.user


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление поста."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        """Добавление формы с instance в контекст."""
        return super().get_context_data(
            form=PostCreateForm(
                instance=get_object_or_404(
                    Post,
                    author=self.request.user)), **kwargs)

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
        return super().get_context_data(deleting=True, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       args=[self.kwargs.get('post_id')])
