from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='HasNoName')
        cls.group = Group.objects.create(
            title='тест группа',
            slug='test_slug',
            description='Описание группы'
        )
        cls.create_post = Post.objects.create(
            text='тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_by_user(self):
        """Работа формы зарегистрирванного пользователя."""
        posts_count = Post.objects.count()
        self.assertEqual(posts_count, 1)
        form_data = {
            'text': 'Какой-то текст',
            'group': self.group
        }
        response = self.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )

        self.assertEqual(
            response.status_code, HTTPStatus.OK)

        self.assertEqual(
            Post.objects.count(), posts_count)
        post = Post.objects.first()
        self.assertEqual(post.author, self.group)
        self.assertEqual(post.group, form_data['group'])
        self.assertEqual(post.text, form_data['Какой-то текст'])

    def test_create_post_by_guest(self):
        """Работа формы незарегистрированного пользователя."""

        posts_count = Post.objects.count()
        post_text_form = {'text': 'Не текст'}
        response = self.client.post(
            reverse('posts:create'), data=post_text_form, follow=True)

        self.assertFalse(
            Post.objects.filter(text='Не текст').exists())
        self.assertEqual(
            response.status_code, HTTPStatus.OK)
        self.assertEqual(
            Post.objects.count(), posts_count)

    def test_post_edit_author(self):
        """Изменение поста зарегистрированным пользователем."""
        group_new = Group.objects.create(
            title='тест группа',
            slug='new-group',
            description='описание группы' * 5,
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'тестовый текст',
            'group': group_new,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    args=(self.create_post.id,)),
            data=form_data,
            follow=True
        )

        edit_post = Post.objects.first()
        response = self.client.get(reverse('posts:group_list',
                                           args=(self.group.slug,)))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(edit_post.author, self.user)
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.group, form_data['group'])
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_post_edit_guest(self):
        """Изменение поста  не зарегистрированным пользователем."""
        Post.objects.all().delete()
        posts_count = Post.objects.count()
        self.assertEqual(posts_count, 0)
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.pk
        }
        response = self.client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )

        self.assertNotEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), posts_count)
