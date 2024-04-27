"""Модуль для фильтрации и аннотации запросов к моделям Django."""
from django.db.models import Count
from django.utils import timezone


def filter_annotate(posts, filter=False, annotate=True):
    """Выбор актуальных публичных постов."""
    if annotate:
        posts = posts.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    if filter:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )
    return posts
