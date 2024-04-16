"""Импорт модулей."""
from django.db.models import Count
from django.utils import timezone


def annotate_comments_and_order(queryset):
    """Добавление аннотации кол-ва комментариев и сортировка по дате."""
    return queryset.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def filter_publ_date(object):
    """Выбор актуальных публичных постов."""
    return object.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )


def filter_publ_date_annotate_comments(object):
    """Выбор актуальных публичных постов."""
    return annotate_comments_and_order(filter_publ_date(object))
