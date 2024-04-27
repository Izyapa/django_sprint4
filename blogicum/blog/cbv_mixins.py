"""Модуль для описания CBV миксинов."""
from django.urls import reverse

from blog.models import Post, Comment

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
                       args=(self.kwargs.get(self.GET_SLUG_PARAM),))


class PostListMixin:
    """Миксин выбора модели Пост."""

    model = Post
    paginate_by = COUNT_PAGINATE
