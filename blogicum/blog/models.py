from django.db import models  # type: ignore
from django.contrib.auth.models import User
from core.models import PublishedModel
from django.urls import reverse


class Category(PublishedModel):
    """Модель Категория."""

    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )

    class Meta:
        """Класс мета."""

        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        """Переопределяем метод str."""
        return self.title


class Location(PublishedModel):
    """Модель Локация."""

    name = models.CharField('Название места', max_length=256)

    class Meta:
        """Класс мета."""

        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        """Переопределяем метод str."""
        return self.name


class Post(PublishedModel):
    """Модель Пост."""

    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text='Если установить дату и время в будущем '
        '— можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        null=True,
        related_name='author',
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='location',
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='category',
        verbose_name='Категория'
    )
    image = models.ImageField('Фото к публикации',
                              upload_to='posts_images',
                              blank=True,
                              )

    class Meta:
        """Класс мета."""

        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        # С помощью нижней кон-ции сделаем сов-ть полей в fields ун-ой
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'text'),
                name='Unique person constraint',
            ),
        )

    def __str__(self) -> str:
        """Переопределяем метод str."""
        return self.title

    def get_absolute_url(self):
        """Возвращаем URL для профиля пользователя, используя его username."""
        return reverse('blog:profile',
                       kwargs={'username': self.author.username})


class Comment(models.Model):
    """Класс коммент."""

    text = models.TextField('Комментарий')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comment',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        """Класс мета."""

        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self) -> str:
        """Переопределяем метод str."""
        return self.text

    def get_absolute_url(self):
        """Возвращаем URL для профиля пользователя, используя его username."""
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.post_id})
