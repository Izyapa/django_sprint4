"""Модуль для описания представлений и форм блога."""
from django.shortcuts import get_object_or_404, redirect

from django.views.generic.edit import FormView
from django.contrib.auth.models import User
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Count

from blog.models import Post, Comment, Category
from .forms import PostCreateForm, CommentForm, CustomProfileForm

from django.utils import timezone
from core.mixins import OnlyAuthorMixin
from django.http import Http404
from django.urls import reverse


class CategoryList(ListView):
    """Вывод постов по категории."""

    template_name = 'blog/category.html'
    model = Post
    paginate_by = 10

    def get_queryset(self):
        """Переопределяем выборку постов по нужной категории."""
        category_slug = self.kwargs.get('category_slug')
        return Post.objects.filter(category__slug=category_slug,
                                   is_published=True,
                                   category__is_published=True,
                                   pub_date__lte=timezone.now(),
                                   ).annotate(
                                       comment_count=Count('comment')
                                       ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        """Добавляем в контекст категорию постов."""
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Category,
                                     slug=category_slug,
                                     is_published=True)
        context['category'] = category
        return context


class Index(ListView):
    """Вывод постов на главную страницу."""

    template_name = 'blog/index.html'
    model = Post
    paginate_by = 10

    def get_queryset(self):
        """Выбор публичных постов, добавляем кол-во комментариев."""
        queryset = super().get_queryset().filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
            ).annotate(
                comment_count=Count('comment')
                ).order_by('-pub_date')
        return queryset


class ProfileDetailView(ListView):
    """Вывод постов на страницу профиля."""

    template_name = 'blog/profile.html'
    model = Post
    paginate_by = 10

    def get_queryset(self):
        """Выбор постов по автору, добавляем кол-во комментариев."""
        user = get_object_or_404(User, username=self.kwargs['username'])
        queryset = super().get_queryset().filter(
            author=user,
        ).annotate(comment_count=Count('comment')).order_by('-pub_date')
        return queryset

    def get_context_data(self, **kwargs):
        """Добавляем в контекст данные профиля."""
        context = super().get_context_data(**kwargs)
        profile = User.objects.get(username=self.kwargs['username'])
        context['profile'] = profile
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста."""

    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Подставим значение поля автор из urls."""
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        """Подставляем в форму значения автора и поста."""
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)

        if (post.is_published and post.category.is_published and
                post.pub_date <= timezone.now()):
            form.instance.post = post
            form.instance.author = self.request.user
            return super().form_valid(form)
        else:
            raise Http404("Post does not exist or cannot be commented on")

    
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


class PostDetailView(DetailView):
    """Просмотр поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        """Добавляем форму и оптимизируем запрос."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related('author')
        )
        return context

    def dispatch(self, request, *args, **kwargs):
        """Проверяем доступность поста для текущего пользователя."""
        post = self.get_object()
        if request.user != post.author:
            if not post.is_published or not post.category.is_published or post.pub_date > timezone.now():
                raise Http404("Post does not exist")
        return super().dispatch(request, *args, **kwargs)


class ProfileUpdateView(LoginRequiredMixin, FormView):
    """Редактирование профиля."""

    form_class = CustomProfileForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:profile')

    def form_valid(self, form):
        """Сохранение формы и перенаправление на страницу профиля."""
        form.save()
        return redirect(reverse_lazy('blog:profile',
                                     kwargs={'username':
                                             self.request.user.username}))

    def get_form_kwargs(self):
        """Получение аргументов для инициализации формы."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        """Получение данных контекста."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user
        context['form'] = self.get_form()

        return context


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление поста."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        """Добавление формы с instance в контекст."""
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id, author=self.request.user)
        context['form'] = PostCreateForm(instance=post)
        return context
    
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
        """?????????????????????????????."""
        context = super().get_context_data(**kwargs)
        context['deleting'] = True
        return context

    def get_success_url(self):
        """?????????????????????????????."""
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.post_id})
