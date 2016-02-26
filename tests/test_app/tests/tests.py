from django.core.urlresolvers import reverse

from .utils import SplinterStaticLiveServerTestCase
from django.contrib.auth.models import User

from luzfcb_djdocuments.models import Documento
from .samples_html import BIG_SAMPLE_HTML


class TestViewEditarDocumento(SplinterStaticLiveServerTestCase):
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

        self.document1_data = {
            'titulo': 'Um documento Bonitão',
            'conteudo': BIG_SAMPLE_HTML,
            'criado_por': self.user1,
            'modificado_por': self.user1
        }
        self.editar_documento_view_name = 'documentos:update2'

        self.documento1 = Documento.objects.create(**self.document1_data)
        self.login_as(username=self.user1_data['username'], password=self.user1_data['password'])

    def test_visit_editar_view_url(self):
        self.visit_url(reverse(self.editar_documento_view_name, kwargs={'pk': self.documento1.pk}))
        self.wait_for_seconds(1)
        botao_salvar = self.browser.find_by_id('salvar')
        botao_salvar.click()
        self.wait_for_seconds(5)
        self.assertTrue(True)
