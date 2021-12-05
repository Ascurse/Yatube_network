import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from posts.models import Post, Group, Comment, Follow

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='Testsuser',
            email='testuser@yatube.ru',
            password='123456'
        )
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug',
        )
        cls.group2 = Group.objects.create(
            title='Тестовое название 2',
            slug='test-slug2',
        )

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client(SERVER_NAME='localhost')
        self.user = self.author
        self.authorised_client = Client(SERVER_NAME='localhost')
        self.authorised_client.force_login(self.user)
        self.user2 = User.objects.create(username='NewUser')
        self.authorised_client2 = Client(SERVER_NAME='localhost')
        self.authorised_client2.force_login(self.user2)

        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='Тестовый комментарий'
        )

    def test_pages_uses_correct_template(self):
        """Страницы используют правильные шаблоны"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:group', args=[self.group.slug]):
                'posts/group_list.html',
            reverse('posts:profile', args=[self.author.username]):
                'posts/profile.html',
            reverse('posts:post_detail', args=[self.post.id]):
                'posts/post_detail.html',
            reverse('posts:post_edit', args=[self.post.id]):
                'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorised_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверка содержимого на главной странице"""
        response = self.authorised_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Тестовый текст'),
        self.assertEqual(post_group_0, 'Тестовое название')
        self.assertEqual(post_image_0, self.post.image.name)

    def test_create_post_show_correct_context(self):
        """Проверка содержимого на странице создания поста"""
        response = self.authorised_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_group_list_show_correct_context(self):
        """Проверка содержимого на странице группы"""
        response = self.authorised_client.get(reverse(
            'posts:group',
            args=[self.group.slug]
        ))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_group_0, 'Тестовое название')
        self.assertEqual(post_image_0, self.post.image.name)

    def test_post_in_correct_url(self):
        """Пост находится в правильных адресах"""
        urls = [
            reverse('posts:index'),
            reverse('posts:group', args=[self.group.slug]),
            reverse('posts:profile', args=[self.author.username]),
        ]
        for value in urls:
            with self.subTest(value=value):
                response = self.authorised_client.get(value)
                self.assertEqual(Post.objects.count(), 1)
                self.assertEqual(self.post,
                                 response.context.get('page_obj')[0])

    def test_post_not_in_incorrect_group(self):
        """Пост не попал в неправильную группу"""
        response = self.authorised_client.get(reverse(
            'posts:group',
            args=[self.group2.slug])
        )
        self.assertNotIn(self.post, response.context.get('page_obj'))

    def test_context_in_profile(self):
        """Проверка содержимого на странице профиля"""
        url = reverse('posts:profile', args=[self.author.username])
        response = self.authorised_client.get(url)
        post = response.context['page_obj'][0]
        author = response.context['author']
        post_text_0 = post.text
        post_author_0 = author.username
        post_image_0 = post.image
        self.assertEqual(post_author_0, 'Testsuser')
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_image_0, self.post.image.name)

    def test_content_in_post_detail(self):
        """Проверка содержимого на странице поста"""
        url = reverse('posts:post_detail', args=[self.post.id])
        response = self.authorised_client.get(url)
        post = response.context['full_post']
        post_text_0 = post.text
        post_image_0 = post.image
        self.assertEqual(post_text_0, 'Тестовый текст')
        self.assertEqual(post_image_0, self.post.image.name)

    def test_content_in_post_edit(self):
        """Проверка содержимого на странице редактирования поста"""
        response = self.authorised_client.get(reverse(
            'posts:post_edit',
            args=[self.post.id])
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_about_uses_correct_template(self):
        """URL об авторе и о технологиях используют правильный шаблон"""
        template_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in template_names.items():
            with self.subTest(template=template):
                response = self.authorised_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_comment_auth_user(self):
        """Комментарий, оставленный авторизированным
           пользователем, появляется на странице
           поста
        """
        post = Post.objects.filter().first()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.authorised_client.post(reverse(
            'posts:add_comment',
            args=[post.id]),
            data=form_data
        )
        get_latest_comment = (
            Comment.objects.filter().last()
        )
        self.assertEqual(form_data['text'], get_latest_comment.text)

    def test_cache_index_page(self):
        """Проверка работы кэша на главной странице"""
        response = self.authorised_client.get(reverse('posts:index'))
        before_clearing = response.content
        Post.objects.create(
            group=PostPagesTest.group,
            text="Новый пост, после кэширования",
            author=User.objects.get(username=self.author.username)
        )
        cache.clear()
        response = self.authorised_client.get(reverse('posts:index'))
        after_clearing = response.content
        self.assertNotEqual(before_clearing, after_clearing)

    def test_auth_user_can_follow_and_unfollow(self):
        """Проверка может ли авторизированный пользователь
           подписываться на авторов и отисываться от них
        """
        self.authorised_client2.get(reverse(
            'posts:profile_follow',
            args=[self.author.username])
        )
        after_follow = Follow.objects.all().filter(
            author_id=self.author,
            user=self.user2
        ).exists()
        self.authorised_client2.get(reverse(
            'posts:profile_unfollow',
            args=[self.author.username])
        )
        after_unfollow = Follow.objects.all().filter(
            author_id=self.author,
            user=self.user2
        ).exists()
        self.assertTrue(after_follow)
        self.assertFalse(after_unfollow)

    def test_follow_index(self):
        """Новая запись появляется в подписках
           и не появляется у не подписанных
        """
        unfollowed = self.authorised_client2.get(reverse(
            'posts:follow_index'
        ))
        self.authorised_client2.get(reverse(
            'posts:profile_follow',
            args=[self.author.username])
        )
        followed = self.authorised_client2.get(reverse(
            'posts:follow_index'
        ))
        self.assertEqual(len(unfollowed.context['page_obj']), 0)
        self.assertNotEqual(len(followed.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Testuser2')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='test-slug'
        )
        posts = [Post(
            author=cls.user,
            group=cls.group,
            text=str(i)) for i in range(13)
        ]
        Post.objects.bulk_create(posts)

    def test_paginator_views(self):
        """На страницах отображается правильное количество объектов"""
        context = [
            len(self.client.get(reverse('posts:index')).context['page_obj']),
            len(self.client.get(reverse(
                'posts:group',
                args=[self.group.slug])).context['page_obj']),
            len(self.client.get(reverse(
                'posts:profile',
                args=[self.user.username])).context['page_obj'])
        ]
        for obj_num in context:
            with self.subTest(obj_num=obj_num):
                self.assertEqual(obj_num, 10)
