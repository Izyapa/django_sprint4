"""Импорт модулей."""
from django.db.models import Count
from django.utils import timezone


def annotate_comments_and_order(posts):
    """Добавление аннотации кол-ва комментариев и сортировка по дате."""
    return posts.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def filter_published_date_annotate_comments(posts):
    """Выбор актуальных публичных постов."""
    return annotate_comments_and_order(posts.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ))
