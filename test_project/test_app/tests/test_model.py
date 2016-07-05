from django.test import TestCase
from djdocuments.models import Documento, TipoDocumento, Assinatura
from django.contrib.auth.models import Group, User


class DocumentoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grupo1 = Group.objects.create(name='grupo1')
        cls.grupo2 = Group.objects.create(name='grupo2')
        cls.grupo3 = Group.objects.create(name='grupo3')

        cls.user1 = User.objects.create(username='user1',
                                        first_name='User1',
                                        last_name='da Silva',
                                        email='user1@user.com',
                                        is_active=True)
        cls.user1.set_password('123')
        cls.user1.groups.add(cls.grupo1)
        cls.user1.groups.add(cls.grupo2)
        cls.user1.save()

        cls.user2 = User.objects.create(username='user2',
                                        first_name='User2',
                                        last_name='Franca',
                                        email='user2@user.com',
                                        is_active=True)
        cls.user2.set_password('123')
        cls.user2.save()
        cls.user3 = User.objects.create(username='user3',
                                        first_name='User3',
                                        last_name='Roots',
                                        email='user3@user.com',
                                        is_active=True)

        cls.user3.set_password('123')
        cls.user3.save()
        cls.tipo_documento1 = TipoDocumento.objects.create(titulo='tipo1', descricao='desc tipo1')
        cls.tipo_documento2 = TipoDocumento.objects.create(titulo='tipo2', descricao='desc tipo2')
        cls.template_doc1 = Documento.objects.create(tipo_documento=cls.tipo_documento1,
                                                     eh_template=True,
                                                     cabecalho='template1',
                                                     rodape='template1',
                                                     conteudo='template1',
                                                     titulo='template1',
                                                     criado_por=cls.user1,
                                                     modificado_por=cls.user1,
                                                     )

        cls.template_doc2 = Documento.objects.create(tipo_documento=cls.tipo_documento2,
                                                     eh_template=True,
                                                     cabecalho='template2',
                                                     rodape='template2',
                                                     conteudo='template2',
                                                     titulo='template2',
                                                     criado_por=cls.user2,
                                                     modificado_por=cls.user3,
                                                     )

    def setUp(self):
        self.documento = Documento(tipo_documento=self.tipo_documento1,
                                   eh_template=True,
                                   cabecalho='template1',
                                   rodape='template1',
                                   conteudo='template1',
                                   titulo='template1',
                                   criado_por=self.user1,
                                   modificado_por=self.user1,
                                   )

        self.documento.save()

    # def criar_documento(self, title="only a test", body="yes, this is only a test"):
    #     return None # Whatever.objects.create(title=title, body=body, created_at=timezone.now())
    def test_criar_documento(self):
        documento = Documento(tipo_documento=self.tipo_documento1,
                              eh_template=True,
                              cabecalho='template1',
                              rodape='template1',
                              conteudo='template1',
                              titulo='template1',
                              criado_por=self.user1,
                              modificado_por=self.user1,
                              )
        documento.save()

        self.assertTrue(documento.pk >= 1)

    def test_adicionar_grupo_assinante(self):
        documento.adicionar_grupos_assinantes([self.grupo1, self.grupo3], self.user1)
        self.assertEqual(documento.assinaturas.count(), 2)

    def test_adicionar_grupo_assinante(self):
        documento = Documento(tipo_documento=self.tipo_documento1,
                              eh_template=True,
                              cabecalho='template1',
                              rodape='template1',
                              conteudo='template1',
                              titulo='template1',
                              criado_por=self.user1,
                              modificado_por=self.user1,
                              )
        documento.save()
        documento.adicionar_grupos_assinantes([self.grupo1, self.grupo3], self.user1)

        self.assertEqual(documento.assinaturas.count(), 2)
