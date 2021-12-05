from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client(SERVER_NAME='localhost')

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='Testsuser',
            email='testuser@yatube.ru',
            password='123456'
        )
        cls.not_author = User.objects.create(
            username='NotAuthor'
        )
        cls.group = Group.objects.create(title='testtitle', slug='test-slug')
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client(SERVER_NAME='localhost')
        self.authorised_client = Client(SERVER_NAME='localhost')
        self.authorised_client.force_login(self.author)
        self.authorised_not_author_client = Client(SERVER_NAME='localhost')
        self.authorised_not_author_client.force_login(self.not_author)

    def test_urls_uses_correct_templates_authorised(self):
        """URL имеют правильные шаблоны"""
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
            f'/profile/{PostURLTests.author.username}/': 'posts/profile.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/posts/{PostURLTests.post.id}/edit/': 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorised_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_url_status_code(self):
        """Проверка кодов ответов от сервера"""
        url_names = [
            ['/', self.guest_client, HTTPStatus.OK],
            [f'/group/{PostURLTests.group.slug}/',
                self.guest_client, HTTPStatus.OK],
            [f'/profile/{PostURLTests.author.username}/',
                self.guest_client, HTTPStatus.OK],
            [f'/posts/{PostURLTests.post.id}/edit/',
                self.guest_client, HTTPStatus.FOUND],
            [f'/posts/{PostURLTests.post.id}/edit/',
                self.authorised_client, HTTPStatus.OK],
            [f'/posts/{PostURLTests.post.id}/',
                self.guest_client, HTTPStatus.OK],
            ['/create/', self.guest_client, HTTPStatus.FOUND],
            ['/create/', self.authorised_client, HTTPStatus.OK]
        ]
        for url, client, status in url_names:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, status)

    def test_post_edit_guest_client_redirect(self):
        """Перенаправление анонимного пользователя
        со страницы редактирования поста
        на страницу логина
        """
        url = reverse('posts:post_edit', args=[self.post.id])
        response = self.guest_client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response,
            '/auth/login/?next=' + url)

    def test_post_edit_author_correct_template(self):
        """Страница редактирования поста доступна автору"""
        response = self.authorised_client.get(reverse(
            'posts:post_edit',
            args=[self.post.id])
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_auth_not_author(self):
        """При попытке редактирования поста НЕ его автором
        перенаправляет на страницу поста
        """
        response = self.authorised_not_author_client.get(
            reverse('posts:post_edit', args=[self.post.id])
        )
        self.assertRedirects(
            response,
            f'/posts/{PostURLTests.post.id}/'
        )

    def test_unexisting_page_404(self):
        """Проверка несуществующей страницы"""
        response = self.guest_client.get('/404/')
        template = 'core/404.html'
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, template)
