from django.utils import timezone


def pub_and_not_fut(queryset):
    """Вспомогательная функция для фильтрации по дате публикации."""
    return queryset.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )
