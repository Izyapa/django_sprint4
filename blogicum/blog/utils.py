"""Импорт модулей.""" 
from django.db.models import Count


def annotate_comments_and_order(queryset):
    """Добавление аннотации кол-ва комментариев и сортировка по дате."""
    return queryset.annotate(
        comment_count=Count('posts_comments')
    ).order_by('-pub_date')
