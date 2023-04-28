from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings

from ..forms import PostForm
from ..models import Post, Group, User

TWENTY = 20

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

    def check_attrs(self, response):
        self.assertEqual(response.author, self.post.author)
        self.assertEqual(response.group, self.post.group)
        self.assertEqual(response.id, self.post.id)
        self.assertEqual(response.text, self.post.text)
        self.assertEqual(response.pub_date, self.post.pub_date)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_context(self):
        """Шаблон Index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        post = Post.objects.select_related('author').all()[0]
        page_obj = response.context['page_obj'][0]

        self.check_attrs(page_obj)
        self.assertIn('page_obj', response.context)
        self.assertEqual(page_obj, post)

    def test_group_list_context(self):
        """Проверка Group list использует правильные данные в контекст."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        post = Post.objects.select_related(
            'author', 'group').filter(group=self.group)[0]

        page_obj = response.context['page_obj'][0]

        self.check_attrs(page_obj)
        self.assertIn('page_obj', response.context)
        self.assertIn('group', response.context)
        self.assertEqual(page_obj, post)

    def test_profile_context(self):
        """Проверка profile использует правильный контекст."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=(self.user.username,)))
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

    def test_post_edit_context(self):
        """Post create page with post_edit использует правильный контекст."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        urls = (
            ('posts:create', None),
            ('posts:post_edit', (self.post.id,)),
        )
        for url, slug in urls:
            reverse_name = reverse(url, args=slug)
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], PostForm)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get(
                            'form').fields.get(value)
                        self.assertIsInstance(form_field, expected)

    def test_post_didnot_fall_into_wrong_group(self):
        """Тест на то, что пост не попал не в ту группу."""
        test_post = Post.objects.create(
            text='этот пост не должен попасть в не нужную группу',
            author=self.user,
            group=self.another_group
        )
        response = self.client.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        page_obj = response.context['page_obj'][settings.ZERO]
        self.assertNotEqual(test_post, page_obj)


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='HasNoName')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        list_of_posts = []

        for page in range(TWENTY):
            list_of_posts.append(
                Post(
                    text=f'Test text №{page}',
                    author=cls.user,
                    group=cls.group,
                ))
        Post.objects.bulk_create(list_of_posts)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator_first_page(self):
        """Проверка корректной работы paginator."""
        list_of_check_page = ('/',
                              '/group/test-slug/',
                              '/profile/HasNoName/'
                              )
        list_of_paginator_page = (
            (('?page=1', settings.POSTS_ON_PAGE),
             ('?page=2', settings.POSTS_ON_PAGE),
             ))

        for page in list_of_check_page:
            for pag in list_of_paginator_page:
                with self.subTest(adress=page):
                    response = self.client.get(page)
                    self.assertEqual(
                        len(response.context['page_obj']),
                        settings.POSTS_ON_PAGE)
                    response = self.client.get(page + '?page=2')
                    self.assertEqual(
                        len(response.context['page_obj']),
                        settings.POSTS_ON_PAGE)
