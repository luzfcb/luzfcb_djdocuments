from django.contrib.auth.models import Group, User
from django.test import TestCase

from djdocuments.models import (
    Assinatura,
    Documento,
    GrupoNaoPodeAssinarException,
    JaEstaAssinado,
    NaoPodeAssinarException,
    TipoDocumento
)


class DocumentoModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.senha = '123'
        cls.grupo1 = Group.objects.create(name='grupo1')
        cls.grupo2 = Group.objects.create(name='grupo2')
        cls.grupo3 = Group.objects.create(name='grupo3')

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
        cls.user3.set_password(cls.senha)
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
                                   eh_template=False,
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
    def criar_documento(self, tipo_documento, criado_por, modificado_por):
        documento = Documento(tipo_documento=tipo_documento,
                              eh_template=False,
                              cabecalho='template1',
                              rodape='template1',
                              conteudo='template1',
                              titulo='template1',
                              criado_por=criado_por,
                              modificado_por=modificado_por,
                              )

        documento.save()
        return documento

    def test_criar_documento(self):
        documento = self.criar_documento(tipo_documento=self.tipo_documento1,
                                         criado_por=self.user1,
                                         modificado_por=self.user1)
        self.assertTrue(documento.pk >= 1)

    def test_adicionar_grupo_assinante(self):
        self.documento.adicionar_grupos_assinantes(self.grupo1, self.user1)
        self.assertEqual(self.documento.assinaturas.count(), 1)

    def test_adicionar_grupo_assinante_ja_adicionado_anteriormente(self):
        self.documento.adicionar_grupos_assinantes(self.grupo1, self.user1)
        self.assertEqual(self.documento.assinaturas.count(), 1)
        self.documento.adicionar_grupos_assinantes(self.grupo1, self.user1)
        self.assertEqual(self.documento.assinaturas.count(), 1)

    def test_adicionar_grupo_assinante_invalido(self):
        self.assertRaises(ValueError,
                          self.documento.adicionar_grupos_assinantes,
                          grupos_assinantes=self.user1,
                          cadastrado_por=self.user1,
                          )
        self.assertEqual(self.documento.assinaturas.count(), 0)

    def test_adicionar_grupos_assinantes(self):
        self.documento.adicionar_grupos_assinantes([self.grupo1, self.grupo3], self.user1)
        self.assertEqual(self.documento.assinaturas.count(), 2)

    def test_usuario_pode_assinar(self):
        documento = self.criar_documento(tipo_documento=self.tipo_documento1,
                                         criado_por=self.user1,
                                         modificado_por=self.user1)
        documento.adicionar_grupos_assinantes([self.grupo1, self.grupo3], self.user1)
        documento.assinar(self.grupo1, self.user1, self.senha)
        assinatura = documento.assinaturas.get(grupo_assinante=self.grupo1, assinado_por=self.user1)

        self.assertTrue(assinatura.esta_assinado)

    def test_usuario_nao_pode_assinar_por_grupo_que_nao_faz_parte(self):
        documento = self.criar_documento(tipo_documento=self.tipo_documento1,
                                         criado_por=self.user1,
                                         modificado_por=self.user1)
        documento.adicionar_grupos_assinantes([self.grupo1, self.grupo2], self.user1)
        self.assertRaises(NaoPodeAssinarException,
                          documento.assinar,
                          grupo_assinante=self.grupo1,
                          usuario_assinante=self.user3,
                          senha=self.senha
                          )

    def test_usuario_nao_pode_assinar_documento_ja_assinado(self):
        documento = self.criar_documento(tipo_documento=self.tipo_documento1,
                                         criado_por=self.user1,
                                         modificado_por=self.user1)
        documento.adicionar_grupos_assinantes([self.grupo1, self.grupo3], self.user1)
        documento.assinar(self.grupo1, self.user1, self.senha)
        assinatura = documento.assinaturas.get(grupo_assinante=self.grupo1, assinado_por=self.user1)
        self.assertTrue(assinatura.esta_assinado)
        self.assertRaises(JaEstaAssinado,
                          documento.assinar,
                          grupo_assinante=self.grupo1,
                          usuario_assinante=self.user1,
                          senha=self.senha
                          )

    def test_grupo_nao_eh_assinante_do_documento(self):
        documento = self.criar_documento(tipo_documento=self.tipo_documento1,
                                         criado_por=self.user1,
                                         modificado_por=self.user1)
        documento.adicionar_grupos_assinantes([self.grupo1, self.grupo2], self.user1)
        self.assertRaises(GrupoNaoPodeAssinarException,
                          documento.assinar,
                          grupo_assinante=self.grupo3,
                          usuario_assinante=self.user1,
                          senha=self.senha
                          )

    def test_usuario_pode_visualizar(self):
        documento = self.criar_documento(tipo_documento=self.tipo_documento1,
                                         criado_por=self.user1,
                                         modificado_por=self.user1)
        documento.adicionar_grupos_assinantes([self.grupo1, self.grupo2], self.user1)
        self.assertTrue(documento.pode_visualizar(self.user1))
        self.assertFalse(documento.pode_visualizar(self.user3))
