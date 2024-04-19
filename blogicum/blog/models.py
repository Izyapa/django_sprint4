"""Модуль для описания моделей."""
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class PublishedModel(models.Model):
    """Абстрактная модель. Добвляет флаг is_published и created_at."""

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
        auto_now=False
    )

    class Meta:

        abstract = True


class Category(PublishedModel):
    """Модель Категория."""

    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        """Переопределяем метод str."""
        return self.title[:10]


class Location(PublishedModel):
    """Модель Локация."""

    name = models.CharField(
        'Название места',
        max_length=256
    )

    class Meta:

        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        """Переопределяем метод str."""
        return self.name[:10]


class Post(PublishedModel):
    """Модель Пост."""

    title = models.CharField(
        'Заголовок',
        max_length=256
    )
    text = models.TextField(
        'Текст'
    )
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем '
        '— можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Фото к публикации',
        upload_to='posts_images',
        blank=True,
    )

    class Meta:

        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'text'),
                name='Unique person constraint',
            ),
        )

    def __str__(self) -> str:
        return self.title[:10]

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.pk})


class Comment(models.Model):
    """Класс коммент."""

    text = models.TextField(
        'Комментарий'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='comments'
    )

    class Meta:
        """Класс мета."""

        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self) -> str:
        """Переопределяем метод str."""
        return self.text[:10]
