from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

# User = get_user_model()

FIRST_PAGE_POSTS = 10
SECOND_PAGE_POSTS = 5
SUM_PAGE = FIRST_PAGE_POSTS + SECOND_PAGE_POSTS


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Opportunity')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание тестовой группы',
        )
        Post.objects.bulk_create([
            Post(author=cls.user,
                 text='Тестовый пост',
                 group=cls.group)
            for i in range(SUM_PAGE)
        ])

    def setUp(self):
        self.aurhorized_client = Client()
        self.aurhorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), FIRST_PAGE_POSTS)

    def test_second_page_contains_five_records(self):
        """Проверка: на второй странице должно быть 5 постов."""
        response = self.client.get(reverse('posts:index'), {'page': 2})
        self.assertEqual(len(response.context['page_obj']), SECOND_PAGE_POSTS)
