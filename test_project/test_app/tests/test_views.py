from django.contrib.auth.models import Group, User
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test.client import RequestFactory
from django.utils import six
from test_plus.test import CBVTestCase, TestCase
from test_project.test_app.models import Processo

from djdocuments import views
from djdocuments.models import (
    Assinatura,
    Documento,
    GrupoNaoPodeAssinarException,
    JaEstaAssinado,
    NaoPodeAssinarException,
    TipoDocumento
)
from djdocuments.views.documentos import create_document_from_document_template


class InjetarDadosIniciaisMixin(object):

    @classmethod
    def setUpTestData(cls):
        cls.senha = '123'
        cls.grupo1 = Group.objects.create(name='grupo1')
        cls.grupo2 = Group.objects.create(name='grupo2')
        cls.grupo3 = Group.objects.create(name='grupo3')
        cls.grupo4 = Group.objects.create(name='grupo4')

        cls.user1 = User.objects.create(username='user1',
                                        first_name='User1',
                                        last_name='da Silva',
                                        email='user1@user.com',
                                        is_active=True)
        cls.user1.set_password(cls.senha)
        cls.user1.groups.add(cls.grupo1)
        cls.user1.groups.add(cls.grupo2)
        cls.user1.save()

        cls.user2 = User.objects.create(username='user2',
                                        first_name='User2',
                                        last_name='Franca',
                                        email='user2@user.com',
                                        is_active=True)
        cls.user2.set_password(cls.senha)
        cls.user2.save()
        cls.user3 = User.objects.create(username='user3',
                                        first_name='User3',
                                        last_name='Roots',
                                        email='user3@user.com',
                                        is_active=True)
        cls.user3.groups.add(cls.grupo3)
        cls.user3.groups.add(cls.grupo4)
        cls.user3.set_password(cls.senha)
        cls.user3.save()
        cls.tipo_documento1 = TipoDocumento.objects.create(titulo='tipo1', descricao='desc tipo1')
        cls.tipo_documento2 = TipoDocumento.objects.create(titulo='tipo2', descricao='desc tipo2')
        cls.template_doc1 = Documento.objects.create(tipo_documento=cls.tipo_documento1,
                                                     eh_template=True,
                                                     cabecalho='cabecalho_template1',
                                                     rodape='rodape_template1',
                                                     conteudo='conteudo_template1',
                                                     titulo='titulo_template1',
                                                     criado_por=cls.user1,
                                                     modificado_por=cls.user1,
                                                     )

        cls.template_doc2 = Documento.objects.create(tipo_documento=cls.tipo_documento2,
                                                     eh_template=True,
                                                     cabecalho='cabecalho_template2',
                                                     rodape='rodape_template2',
                                                     conteudo='conteudo_template2',
                                                     titulo='titulo_template2',
                                                     criado_por=cls.user2,
                                                     modificado_por=cls.user3,
                                                     )
        cls.documento_criar_named_view = 'documentos:create'


class DocumentCreateTestCase(InjetarDadosIniciaisMixin, TestCase):
    # def setUp(self):
    #     self.documento = Documento(tipo_documento=self.tipo_documento1,
    #                                eh_template=False,
    #                                cabecalho='template1',
    #                                rodape='template1',
    #                                conteudo='template1',
    #                                titulo='template1',
    #                                criado_por=self.user1,
    #                                modificado_por=self.user1,
    #                                )
    #
    # #     self.documento.save()
    # def test_restrictions(self):
    #     self.assertLoginRequired(self.documento_criar_named_view)

    def test_get_view(self):
        with self.login(username=self.user1.username, password=self.senha):
            response = self.get(self.documento_criar_named_view)
            self.response_200(response)

    # def test_form(self):
    #     response = self.reverse(self.documento_criar_named_view)
    #     a = response
    #
    def test_with_vinculate_parameters(self):
        with self.login(username=self.user1.username, password=self.senha):
            parametros_get = {'v': 'test_vinculate_view', 'to': 'test_vinculate_pk'}
            response = self.client.get(reverse(self.documento_criar_named_view), parametros_get)
            self.assertDictContainsSubset(parametros_get, response.context_data['view'].request.GET)

    # def test_with_vinculate_only_to_parameter(self):
    #     parametros_get = {'to': 'test_vinculate_pk'}
    #     response = self.client.get(reverse(self.documento_criar_named_view))
    #     self.assertDictContainsSubset(parametros_get, response.context_data['view'].request.GET)

    def test_not_with_vinculate_parameters(self):
        with self.login(username=self.user1.username, password=self.senha):
            parametros_get = {'v': None, 'to': None}
            response = self.client.get(reverse(self.documento_criar_named_view))
            parametros_processador = response.context_data['view'].request.GET.keys()
            for key in parametros_get.keys():
                self.assertNotIn(key, parametros_processador)

    def test_create_document(self):
        data = {
            'grupo': self.grupo1.pk,
            'tipo_documento': self.tipo_documento1.pk,
            'modelo_documento': self.template_doc1.pk,
            'assunto': 'teste1-create_document'
        }
        with self.login(username=self.user1.username, password=self.senha):
            # follow=True habilita o processamento do redirecionamento
            response = self.client.post(reverse(self.documento_criar_named_view), data=data, follow=True)

            # obter o documento recem criado
            documento = Documento.objects.get(assunto='teste1-create_document')
            self.assertEqual(documento.criado_por, self.user1)
            self.assertEqual(documento.modificado_por, self.user1)

            self.assertEqual(documento.cabecalho, 'cabecalho_template1')
            self.assertEqual(documento.rodape, 'rodape_template1')
            self.assertEqual(documento.conteudo, 'conteudo_template1')
            self.assertEqual(documento.titulo, 'titulo_template1')

            self.assertEqual(documento.tipo_documento, self.tipo_documento1)

            # verifica se houve 1 redirecionamento
            self.assertEqual(len(response.redirect_chain), 1)

            # verifica redirecionamentos view DocumentoCriar para DocumentoEditor
            self.assertEqual(response.redirect_chain[0][0], "http://testserver{}".format(
                reverse('documentos:editar', kwargs={'slug': documento.pk_uuid})))
            self.assertEqual(response.redirect_chain[0][1], 301)

    def test_create_document_with_vincular(self):
        processo = Processo.objects.create(nome='processo1')
        parametros_get = {'v': 'documento_processo_vincular', 'to': processo.pk}
        qd = QueryDict(mutable=True)
        qd.update(parametros_get)
        url_com_parametro_get = '{}?{}'.format(reverse(self.documento_criar_named_view), qd.urlencode())

        data = {
            'grupo': self.grupo1.pk,
            'tipo_documento': self.tipo_documento1.pk,
            'modelo_documento': self.template_doc1.pk,
            'assunto': 'teste1-create_document'
        }

        with self.login(username=self.user1.username, password=self.senha):
            # verifica se processo nao possui documento vinculado
            self.assertFalse(processo.documentos.exists())
            response = self.client.post(url_com_parametro_get, data=data, follow=True)
            # obter o documento recem criado
            documento = Documento.objects.get(assunto='teste1-create_document')
            self.assertEqual(documento.criado_por, self.user1)
            self.assertEqual(documento.modificado_por, self.user1)

            self.assertEqual(documento.cabecalho, 'cabecalho_template1')
            self.assertEqual(documento.rodape, 'rodape_template1')
            self.assertEqual(documento.conteudo, 'conteudo_template1')
            self.assertEqual(documento.titulo, 'titulo_template1')

            self.assertEqual(documento.tipo_documento, self.tipo_documento1)

            self.assertEqual(documento.grupo_dono, self.grupo1)
            self.assertIn(self.grupo1, documento.grupos_assinates.all())

            # verifica se processo possui documento vinculado
            self.assertTrue(processo.documentos.exists())
            # verifica se houve 2 redirecionamentos
            self.assertEqual(len(response.redirect_chain), 2)

            # verifica redirecionamentos view djdocuments.DocumentoCriar para test_app.DocumentoProcessoVinculateView
            self.assertEqual(response.redirect_chain[0][0], "http://testserver{}".format(
                reverse('documento_processo_vincular', kwargs={'document_pk': documento.pk, 'pk': processo.pk})))
            self.assertEqual(response.redirect_chain[0][1], 301)
            # verifica redirecionamentos view test_appDocumentoProcessoVinculateView para DocumentoEditor
            self.assertEqual(response.redirect_chain[1][0], "http://testserver{}".format(
                reverse('documentos:editar', kwargs={'slug': documento.pk_uuid})))
            self.assertEqual(response.redirect_chain[1][1], 301)


class DocumentAssinaturasTestCase(InjetarDadosIniciaisMixin, TestCase):
    documento1 = None
    documento_assinaturas_named_url = 'documentos:assinaturas'
    documento_adicionar_assinantes_named_url = 'documentos:adicionar_assinantes'
    documento_remover_assinatura_named_url = 'documentos:remover_assinatura'

    def setUp(self):
        super(DocumentAssinaturasTestCase, self).setUp()

        self.documento1 = create_document_from_document_template(current_user=self.user1,
                                                                 grupo=self.grupo1,
                                                                 documento_template=self.template_doc1,
                                                                 assunto='teste1-create_document'
                                                                 )

    def test_get_assinaturas_view(self):
        with self.login(username=self.user1.username, password=self.senha):
            response = self.get(reverse(self.documento_assinaturas_named_url, kwargs={'slug': self.documento1.pk_uuid}))
            self.response_200(response)

    def test_get_assinaturas_view_sem_estar_logado(self):
        assinaturas_documento_url = reverse(self.documento_assinaturas_named_url,
                                            kwargs={'slug': self.documento1.pk_uuid})
        response = self.get(assinaturas_documento_url,
                            follow=True)
        self.assertRedirects(response, expected_url='accounts/login/?next={}'.format(assinaturas_documento_url))

    def test_documento_recem_criado_possui_como_assinante_o_grupo_dono_do_documento(self):
        documento = create_document_from_document_template(current_user=self.user1,
                                                           grupo=self.grupo1,
                                                           documento_template=self.template_doc1,
                                                           assunto='teste1-create_document'
                                                           )
        self.assertEqual(documento.grupo_dono, self.grupo1)
        self.assertIn(self.grupo1, documento.grupos_assinates.all())

    def test_adicionar_1_grupo_assinantes(self):
        with self.login(username=self.user1.username, password=self.senha):
            assinaturas_documento_url = reverse(self.documento_assinaturas_named_url,
                                                kwargs={'slug': self.documento1.pk_uuid})
            adicionar_assinantes_url = reverse(self.documento_adicionar_assinantes_named_url,
                                               kwargs={'slug': self.documento1.pk_uuid})
            response = self.get(adicionar_assinantes_url)
            self.response_200(response)

            data = {
                'grupo_para_adicionar': [self.grupo2.pk]
            }

            response = self.client.post(adicionar_assinantes_url, data=data, follow=True)
            self.response_200(response)
            # verifica se contem os valores esperados
            self.assertEqual(self.documento1.grupo_dono, self.grupo1)
            self.assertIn(self.grupo1, self.documento1.grupos_assinates.all())
            self.assertIn(self.grupo2, self.documento1.grupos_assinates.all())
            self.assertNotIn(self.grupo3, self.documento1.grupos_assinates.all())

            self.assertRedirects(response, expected_url=assinaturas_documento_url)

    def test_adicionar_2_grupo_assinantes(self):
        with self.login(username=self.user1.username, password=self.senha):
            assinaturas_documento_url = reverse(self.documento_assinaturas_named_url,
                                                kwargs={'slug': self.documento1.pk_uuid})
            adicionar_assinantes_url = reverse(self.documento_adicionar_assinantes_named_url,
                                               kwargs={'slug': self.documento1.pk_uuid})
            response = self.get(adicionar_assinantes_url)
            self.response_200(response)

            data = {
                'grupo_para_adicionar': [self.grupo2.pk, self.grupo3.pk]
            }

            response = self.client.post(adicionar_assinantes_url, data=data, follow=True)
            self.response_200(response)
            # verifica se contem os valores esperados
            self.assertEqual(self.documento1.grupo_dono, self.grupo1)
            self.assertIn(self.grupo1, self.documento1.grupos_assinates.all())
            self.assertIn(self.grupo2, self.documento1.grupos_assinates.all())
            self.assertIn(self.grupo3, self.documento1.grupos_assinates.all())

            self.assertRedirects(response, expected_url=assinaturas_documento_url)

    def test_adicionar_grupo_assinantes_ja_adicionado_previamente(self):
        with self.login(username=self.user1.username, password=self.senha):
            assinaturas_documento_url = reverse(self.documento_assinaturas_named_url,
                                                kwargs={'slug': self.documento1.pk_uuid})
            adicionar_assinantes_url = reverse(self.documento_adicionar_assinantes_named_url,
                                               kwargs={'slug': self.documento1.pk_uuid})
            response = self.get(adicionar_assinantes_url)
            self.response_200(response)

            data = {
                'grupo_para_adicionar': [self.grupo2.pk]
            }

            response = self.client.post(adicionar_assinantes_url, data=data, follow=True)
            self.response_200(response)
            # verifica se contem os valores esperados
            self.assertEqual(self.documento1.grupo_dono, self.grupo1)
            self.assertIn(self.grupo1, self.documento1.grupos_assinates.all())
            self.assertIn(self.grupo2, self.documento1.grupos_assinates.all())
            self.assertNotIn(self.grupo3, self.documento1.grupos_assinates.all())
            self.assertRedirects(response, expected_url=assinaturas_documento_url)

            response = self.client.post(adicionar_assinantes_url, data=data, follow=True)
            self.response_200(response)
            self.assertEqual(self.documento1.assinaturas.filter(grupo_assinante=self.grupo2.pk).count(), 1)

    # def test_remover_grupo_assinante_ja_adicionado_previamente(self):
    #     with self.login(username=self.user1.username, password=self.senha):
    #         self.documento1.adicionar_grupos_assinantes(grupos_assinantes=self.grupo2, cadastrado_por=self.user1)
    #         remover_assinatura_named_url = reverse(self.documento_remover_assinatura_named_url,
    #                                                kwargs={'document_slug': self.documento1.pk_uuid,
    #                                                        'pk': self.grupo1.pk})
    #         # adicionar_assinantes_url = reverse(self.documento_adicionar_assinantes_named_url,
    #         #                                    kwargs={'slug': self.documento1.pk_uuid})
    #         response = self.get(remover_assinatura_named_url)
    #         self.assertIn(self.grupo1, self.documento1.grupos_assinates.all())
    #         data = {
    #             'grupo_para_adicionar': [self.grupo2.pk]
    #         }
    #
    #         response = self.client.post(remover_assinatura_named_url, follow=True)
    #         self.assertNotIn(self.grupo1, self.documento1.grupos_assinates.all())
