from django.test import Client, TestCase
from django.urls import reverse
from http import HTTPStatus


from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.user1 = User.objects.create_user(username='user1')
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
        cls.url_templates = {
            'posts/index.html': '/',
            'posts/profile.html': f'/profile/{cls.user.username}/',
            'posts/group_list.html': f'/group/{cls.group.slug}/',
            'posts/post_detail.html': f'/posts/{cls.post.id}/',
            'posts/create_post.html': '/create/',
        }

    def setUp(self):
        self.author = Client()
        self.author.force_login(self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)


    def test_for_matching_reverse_with_hardcore(self):
        '''тест проверки соответствия, что прямые - хардкод ссылки
        равны полученным по reverse(name)'''
        reverse_for_url = (
            ('posts:index', None, '/'),
            ('posts:group_list',
             (self.group.slug,),
             f'/group/{self.group.slug}/'
             ),
            ('posts:profile',
             (self.user.username,),
             f'/profile/{self.user.username}/'
             ),
            ('posts:post_detail',
             (self.post.id,),
             f'/posts/{self.post.id}/'
             ),
            ('posts:post_edit',
             (self.post.id,),
             f'/posts/{self.post.id}/edit/'
             ),
            ('posts:create', None, '/create/'),
        )
        for name, args, url in reverse_for_url:
            with self.subTest(name=name):
                reverse_url = reverse(name, args=args)
                self.assertEqual(reverse_url, url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:group_list', (self.group.slug,), 'posts/group_list.html'),
            ('posts:profile', (self.user.username,), 'posts/profile.html'),
            ('posts:post_detail', (self.post.id,), 'posts/post_detail.html'),
            ('posts:post_edit', (self.post.id,), 'posts/create_post.html'),
            ('posts:create', None, 'posts/create_post.html'),
        )
        for name, args, template in templates_url_names:
            with self.subTest(name=name):
                response = self.author.get(reverse(name, args=args))
                self.assertTemplateUsed(response, template)

    def test_urls_access_anonim(self):
        """URL-адрес доступность для анонимного пользователя"""
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest(reverse_name=reverse_name):
                if reverse_name == reverse('post_create'):
                    response = self.anonim_user.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                    self.assertRedirects(response, '/auth/login/?next=/create/')
                elif reverse_name == reverse(
                        'add_comment', kwargs={'post_id': self.post.id}):
                    response = self.anonim_user.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                    self.assertRedirects(response,
                                         f'/auth/login/?next='
                                         f'/posts/')
                else:
                    response = self.anonim_user.get(reverse_name)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.anonim_user.get(f'/posts/'
                                        f'{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
