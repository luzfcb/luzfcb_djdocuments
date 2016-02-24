from .utils import SplinterStaticLiveServerTestCase
from django.contrib.auth.models import User


class NovoTeste(SplinterStaticLiveServerTestCase):
    use_virtual_display = False

    def setUp(self):
        self.user1_data = {
            'username': 'admin',
            'email': 'admin@admin.com',
            'password': 'admin',
            'first_name': 'Admin',
            'last_name': 'Root'
        }

        self.user1 = User.objects.create_superuser(**self.user1_data)
        self.login_as(username=self.user1_data['username'], password=self.user1_data['password'])

    def test_create_document(self):
        self.browser.visit()
        self.assertTrue(True)
