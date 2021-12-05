from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Group, Post

User = get_user_model()


class ModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст'
        )

    def test_models_have_correct_objects_names(self):
        """Проверка работы __str__."""
        group = ModelTests.group
        title = group.title
        self.assertEqual(title, str(group))

    def test_models_have_correct_object_post(self):
        post = ModelTests.post
        expected_text = post.text[:15]
        self.assertEqual(expected_text, str(post))

    def test_models_verbose_name(self):
        """verbose_name совпадает с ожидаемым."""
        post = ModelTests.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_models_help_texts(self):
        """help_text совпадает с ожидаемым."""
        post = ModelTests.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
