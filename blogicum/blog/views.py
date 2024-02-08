from django.shortcuts import get_object_or_404, render, redirect
from django.db import models
from blog.models import Post, Category, Comment
from blog.querysets import pub_and_not_fut
from django.contrib.auth.decorators import login_required
from .forms import BlogCreateForm, CommentForm
from django.views.generic.edit import FormView
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth.forms import UserChangeForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.contrib.auth.models import User
from django.db.models import Count

def category_posts(request, category_slug):
    """Блог категории."""
    posts = pub_and_not_fut(
        Post.objects.filter(
            category__slug=category_slug,
        )
    )
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    context = {
        'post_list': posts,
        'category': category
    }
    return render(request, 'blog/category.html', context)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related('author')
        )
        return context


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        posts = Post.objects.filter(author=user).order_by('-pub_date')
        annotated_posts = posts.annotate(comment_count=Count('comment'))
        context['page_obj'] = annotated_posts
        return context


class ProfileUpdateView(LoginRequiredMixin, FormView):
    form_class = UserChangeForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:profile')

    def form_valid(self, form):
        """func."""
        form.save()
        return redirect(reverse_lazy('blog:profile',
                                     kwargs={'username': self.request.user.username}))

    def get_form_kwargs(self):
        """func."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        """func."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user
        context['form'] = self.get_form()

        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = BlogCreateForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """func."""
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:list')

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = BlogCreateForm

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)


class Index(ListView):
    template_name = 'blog/index.html'
    model = Post
    paginate_by = 10

    def get_queryset(self):
        # Аннотируйте количество комментариев для каждого поста
        return Post.objects.filter(is_published=1).annotate(comment_count=models.Count('comment'))


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.comment = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    context_object_name = 'comment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editing'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.post.pk})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    context_object_name = 'comment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deleting'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.post.pk})
