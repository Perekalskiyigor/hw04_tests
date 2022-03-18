from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def setUp(self):
        self.user_guest = Client()


class StaticURLTests(TestCase):
    def test_about_url_uses_correct_template(self):
        """URL-адрес использует соответствующие шаблоны about/*."""
        templates_url_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.user_guest.get(address)
                self.assertTemplateUsed(response, template)
