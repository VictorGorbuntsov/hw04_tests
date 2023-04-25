from django.test import TestCase, Client


from ..models import Group, Post, User


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

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url_location(self):
        """Страница / доступна любому пользователю."""
        resource = self.client.get(f'/group/{self.group.slug}/')
        self.assertEqual(resource.status_code, 200)

    def test_profile_url_lacation(self):
        """Страница / доступна любому пользователю."""
        resource = self.client.get(f'/profile/{self.user}/')
        self.assertEqual(resource.status_code, 200)

    def test_post_id_url_location(self):
        """Страница / доступна любому пользователю."""
        resource = self.client.get(f'/posts/{self.post.id}/')
        self.assertEqual(resource.status_code, 200)

    def test_edit_url_location(self):
        """Страница / доступна автору поста."""
        resource = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(resource.status_code, 200)

    def test_create_url_location(self):
        """Страница / доступна авторизованому пользователю."""
        resource = self.authorized_client.get('/create/')
        self.assertEqual(resource.status_code, 200)

    def test_404_url_locations(self):
        """Не доступная страница"""
        resource = self.client.get('/404/')
        self.assertEqual(resource.status_code, 404)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        for address, templates in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, templates)
