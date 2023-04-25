from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings

from ..models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовый текст'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': 'HasNoName'}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': settings.NUMBER_ONE}
                    ): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': settings.NUMBER_ONE}
                    ): 'posts/create_post.html',
            reverse('posts:create'): 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Шаблон Index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post = Post.objects.select_related('author').all()[0]
        page_obj = response.context['page_obj'][0]
        self.assertIn('page_obj', response.context)
        self.assertEqual(page_obj, post)

    def test_group_list_context(self):
        """Проверка Group list использует правильные данные в контекст."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        post = Post.objects.select_related(
            'author', 'group').filter(group=self.group)[0]

        page_obj = response.context['page_obj'][0]

        self.assertIn('page_obj', response.context)
        self.assertIn('group', response.context)
        self.assertEqual(page_obj, post)

    def test_profile_context(self):
        """Проверка profile использует правильный контекст."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'HasNoName'}))
        post = Post.objects.select_related(
            'author', 'group').filter(author=self.user)[0]
        page_obj = response.context['page_obj'][0]

        self.assertIn('page_obj', response.context)
        self.assertIn('author', response.context)
        self.assertEqual(page_obj, post)

    def test_post_detail_context(self):
        """Проверка Post detail использует правильный контекст."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))

        post = response.context['post']

        self.assertEqual(post, self.post)

    def test_post_create_context(self):
        """Post create page и post_create использует правильный контекст."""
        response = self.authorized_client.get(reverse('posts:create'))

        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField}


        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        """Post create page with post_edit использует правильный контекст."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        form_field_text = response.context.get('form')['text'].value()
        form_field_group = response.context.get('form')['group'].value()

        self.assertEqual(form_field_text, self.post.text)
        self.assertEqual(form_field_group, self.post.group.pk)


        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        for page in range(10):
            Post.objects.create(
                text=f'Test text №{page}',
                author=cls.user,
                group=cls.group,
            )

    def test_paginator_first_page(self):
        """Проверка корректной работы paginator."""
        list_of_check_page = ['/', '/group/test-slug/', '/profile/HasNoName/']
        for page in list_of_check_page:
            with self.subTest(adress=page):
                response = self.client.get(page)
                self.assertEqual(
                    len(response.context['page_obj']), settings.POSTS_ON_PAGE)
                response = self.client.get(page + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.POSTS_ON_PAGE)
