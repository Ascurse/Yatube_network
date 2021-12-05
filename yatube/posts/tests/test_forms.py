import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from posts.forms import PostForm
from posts.models import Group, Post, User
from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='Testuser',
            email='testuser1@yatube.ru',
            password='123456'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа1',
            slug='test-slug11',
        )

        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client(SERVER_NAME='localhost')
        self.user = self.author
        self.authorised_client = Client(SERVER_NAME='localhost')
        self.authorised_client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )

    def test_create_post(self):
        """Создается новая запись в БД"""
        form_context = {
            'text': 'Новый текст',
            'group': self.group.id,
            'image': self.uploaded,
        }
        count_posts = Post.objects.count()
        response = self.authorised_client.post(reverse(
            'posts:post_create'),
            data=form_context
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse(
            'posts:profile',
            args=[self.author.username])
        )
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertTrue(Post.objects.filter(
            text='Новый текст',
            group=PostFormTests.group,
            image='posts/small.gif').exists())

    def test_edit_post(self):
        """Изменение поста в БД"""
        form_context = {
            'text': 'Отредактированный текст',
            'group': self.group.id,
        }
        self.authorised_client.post(reverse(
            'posts:post_edit',
            args=[self.post.id]),
            data=form_context,
        )
        self.assertTrue(Post.objects.filter(
            text='Отредактированный текст',
            group=PostFormTests.group).exists()
        )
