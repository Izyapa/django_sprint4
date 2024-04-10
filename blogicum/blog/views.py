"""Модуль для описания представлений и форм блога."""
from django.contrib.auth.mixins import LoginRequiredMixin  # type: ignore
from django.contrib.auth.models import User  # type: ignore
from django.http import Http404  # type: ignore
from django.shortcuts import get_object_or_404, redirect  # type: ignore
from django.urls import reverse, reverse_lazy  # type: ignore
from django.utils import timezone  # type: ignore
from django.views.generic import (  # type: ignore
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.views.generic.edit import FormView  # type: ignore

from blog.forms import PostCreateForm, CommentForm, ProfileForm
from blog.models import Post, Comment, Category
from blog.utils import annotate_comments_and_order
from core.mixins import OnlyAuthorMixin

COUNT_PAGINATE = 10


class CategoryList(ListView):
    """Вывод постов по категории."""

    template_name = 'blog/category.html'
    model = Post
    paginate_by = COUNT_PAGINATE

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        category = get_object_or_404(Category, slug=category_slug,
                                     is_published=True)
        queryset = category.posts_at_category.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )
        return annotate_comments_and_order(queryset)

    def get_context_data(self, **kwargs):
        """Добавляем в контекст категорию постов."""
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category,
                                     slug=category_slug,
                                     is_published=True)
        return super().get_context_data(category=category, **kwargs)


class Index(ListView):
    """Вывод постов на главную страницу."""

    template_name = 'blog/index.html'
    model = Post
    paginate_by = COUNT_PAGINATE

    def get_queryset(self):
        """Выбор публичных постов, добавляем кол-во комментариев."""
        queryset = super().get_queryset().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
        return annotate_comments_and_order(queryset)


class ProfileDetailView(ListView):
    """Вывод постов на страницу профиля."""

    template_name = 'blog/profile.html'
    model = Post
    paginate_by = COUNT_PAGINATE

    def get_queryset(self):
        """Выбор постов по автору, добавляем кол-во комментариев."""
        user = get_object_or_404(User, username=self.kwargs['username'])
        return annotate_comments_and_order(user.posts_written.all())

    def get_context_data(self, **kwargs):
        """Добавляем в контекст данные профиля."""
        profile = get_object_or_404(User, username=self.kwargs['username'])
        return super().get_context_data(profile=profile, **kwargs)


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
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        """Подставляем в форму значения автора и поста."""
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        if (post.is_published and post.category.is_published
                and post.pub_date <= timezone.now()):
            form.instance.post = post
            form.instance.author = self.request.user
            return super().form_valid(form)

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs.get('post_id')})


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
                       kwargs={'post_id': self.kwargs.get('post_id')})


class PostDetailView(DetailView):
    """Просмотр поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        """Добавляем форму и оптимизируем запрос."""
        comments = (
            self.object.posts_comments.select_related('author')
        )
        return super().get_context_data(form=CommentForm(),
                                        comments=comments,
                                        **kwargs)

    def check_post_availability(self, post):
        """Проверка доступности поста для текущего пользователя."""
        if not (post.is_published and post.category.is_published
                and post.pub_date <= timezone.now()):
            raise Http404("Post does not exist")

    def dispatch(self, request, *args, **kwargs):
        """Проверяем доступность поста для текущего пользователя."""
        post = self.get_object()
        if request.user != post.author:
            self.check_post_availability(post)
        return super().dispatch(request, *args, **kwargs)


class ProfileUpdateView(LoginRequiredMixin, FormView):
    """Редактирование профиля."""

    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        """Получение URL для перенаправления при успешной валидации формы."""
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})

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
