import tempfile
from django.test import Client, TestCase
from django.core.cache import cache
from django.urls import reverse
from django.conf import settings

from ..models import Follow, Post, User

NUM_POSTS_TEST = settings.NUM_POSTS_PER_PAGE + 3
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
# User = get_user_model() получаем из модели


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_autor = User.objects.create(username='IvanIvanov')
        cls.post_follower = User.objects.create(username='PetrPetrov')
        cls.post = Post.objects.create(
            text='Тестовый текст проверяем подписку',
            author=cls.post_autor,
        )

    def setUp(self):
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(self.post_follower)
        self.follower_client = Client()
        self.follower_client.force_login(self.post_autor)

    def test_subscribe(self):
        """Валидация подписки на пользователя."""
        follow_count = Follow.objects.count()
        self.follower_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post_follower}
            )
        )
        follow = Follow.objects.all().latest('id')
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertEqual(follow.author_id, self.post_follower.id)
        self.assertEqual(follow.user_id, self.post_autor.id)

    def test_posts_subscribe(self):
        """Валидация записей у тех, кто подписан."""
        post = Post.objects.create(
            author=self.post_autor,
            text="Тестовый текст проверяем подписку"
        )
        Follow.objects.create(
            user=self.post_follower,
            author=self.post_autor
        )
        response = self.author_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(post, response.context['page_obj'].object_list)

    def test_unsubscribe(self):
        """Валидация отписки от пользователя."""
        Follow.objects.create(
            user=self.post_autor,
            author=self.post_follower
        )
        count_follow = Follow.objects.count()
        self.follower_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.post_follower}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow - 1)

    def test_posts_unsubscribe(self):
        """Валидация записей у тех, кто не подписан."""
        post = Post.objects.create(
            author=self.post_autor,
            text="Тестовый текст проверяем отписку"
        )
        response = self.author_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(post, response.context['page_obj'].object_list)
