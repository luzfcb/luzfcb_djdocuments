# # -*- coding: utf-8 -*-
# from django.contrib.auth.models import User
# from django.core.urlresolvers import reverse
#
# from djdocuments.models import Documento
#
# from .samples_html import BIG_SAMPLE_HTML
# from .utils import SplinterStaticLiveServerTestCase
#
#
# class TestViewEditarDocumento(SplinterStaticLiveServerTestCase):
#     splinter_driver = 'chrome'
#     use_virtual_display = True
#     # splinter_driver = 'phantomjs'
#
#     def setUp(self):
#         self.user1_data = {
#             'username': 'admin',
#             'email': 'admin@admin.com',
#             'password': 'admin',
#             'first_name': 'Admin',
#             'last_name': 'Root'
#         }
#         self.user1 = User.objects.create_superuser(**self.user1_data)
#
#         self.document1_data = {
#             'titulo': 'Um documento Bonitão',
#             'conteudo': BIG_SAMPLE_HTML,
#             'criado_por': self.user1,
#             'modificado_por': self.user1
#         }
#         self.editar_documento_view_name = 'documentos:editar'
#
#         self.documento1 = Documento.objects.create(**self.document1_data)
#         self.login_as(username=self.user1_data['username'], password=self.user1_data['password'])
#
#     def test_visit_editar_view_url(self):
#         self.visit_url(reverse(self.editar_documento_view_name, kwargs={'pk': self.documento1.pk}))
#         self.wait_for_seconds(1)
#
#         js = """
#         for (var instance in CKEDITOR.instances) {
#             if (CKEDITOR.instances.hasOwnProperty(instance)) {
#                 CKEDITOR.instances[instance].setData('%s');
#                 setTimeout(function(){},2000);
#                 $('#salvar').click();
#             }
#
#         }
#         """ % "Adeus mundo"
#         self.browser.execute_script(js)
#         self.wait_for_seconds(1)
#         botao_salvar = self.browser.find_by_id('salvar')
#         botao_salvar.click()
#         self.wait_for_seconds(5)
#         # div_cke_id_document_cabecalho = self.browser.find_by_id('cke_id_document-cabecalho')
#         # with self.browser.get_iframe('iframemodal') as iframe:
#         #     iframe.do_stuff()
#
#         self.wait_for_seconds(5)
#         self.assertTrue(True)
