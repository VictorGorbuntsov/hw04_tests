from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='тест группа',
            slug='test_slug',
            description='Описание группы'
        )

    def test_create_post_by_user(self):
        """Работа формы зарегистрирванного пользователя."""

        posts_count = Post.objects.count()
        post_text_form = {'text': 'Какой-то текст'}
        response = self.authorized_client.post(
            reverse('posts:create'), data=post_text_form, follow=True)

        self.assertTrue(
            Post.objects.filter(text='Какой-то текст').exists())
        self.assertEqual(
            response.status_code, 200)
        self.assertRedirects(
            response, reverse('posts:profile',
                              kwargs={'username': 'HasNoName'}))
        self.assertEqual(
            Post.objects.count(), posts_count + 1)

    def test_create_post_by_guest(self):
        """Работа формы незарегистрированного пользователя."""

        posts_count = Post.objects.count()
        post_text_form = {'text': 'Не текст'}
        response = self.client.post(
            reverse('posts:create'), data=post_text_form, follow=True)

        self.assertFalse(
            Post.objects.filter(text='Не текст').exists())
        self.assertEqual(
            response.status_code, 200)
        self.assertEqual(
            Post.objects.count(), posts_count)

    def test_post_edit_author(self):
        """Изменение поста зарегистрированным пользователем."""

        create_post = Post.objects.create(
            text='Some Text',
            author=self.user,
            group=self.group
        )
        post_text_form = {'text': 'Измененный текст', 'group': self.group.pk}

        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': create_post.id}), data=post_text_form)

        edit_post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(edit_post.author, self.user)
        self.assertEqual(edit_post.text, 'Измененный текст')
        self.assertEqual(edit_post.group.pk, self.group.pk)

    def test_post_edit_guest(self):
        """Изменение поста  не зарегистрированным пользователем."""

        create_post = Post.objects.create(
            text='Some Text',
            author=self.user,
            group=self.group
        )

        post_text_form = {'text': 'Измененный текст', 'group': self.group.pk}

        response = self.client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': create_post.id}), data=post_text_form)

        edit_post = Post.objects.select_related('group', 'author').get()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(edit_post.author, self.user)
        self.assertEqual(edit_post.text, 'Some Text')
        self.assertEqual(edit_post.group.pk, self.group.pk)
