from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreateModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200, null=False,
        verbose_name="Название сообщества",
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="url адрес сообщества",
    )
    description = models.TextField(
        max_length=600,
        verbose_name="Описание сообщества",
    )

    def __str__(self) -> str:
        return self.title


class Post(CreateModel):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        related_name='posts',
        help_text='Выберите группу',
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']


class Comment(CreateModel):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        'Текст',
        help_text='Текст нового комментария',
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name="follower",
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name="following",
        on_delete=models.CASCADE
    )
