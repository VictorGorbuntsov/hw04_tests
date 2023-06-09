from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=settings.THIRTY,
        related_name='posts',
        verbose_name='Группа',
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ('-pub_date', 'author',)

    def __str__(self):
        return self.text[:settings.THIRTY]


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Создание группы')
    slug = models.SlugField(unique=True, verbose_name='Параметр')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Заголовок'
        verbose_name_plural = 'Заголовки'

    def __str__(self):
        return self.title
