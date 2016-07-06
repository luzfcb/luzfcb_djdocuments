# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import logging
from datetime import datetime

from django.contrib.auth.hashers import SHA1PasswordHasher
from django.db import models
from django.db.models import Q, Max
from django.utils.encoding import python_2_unicode_compatible
from simple_history.models import HistoricalRecords
from simple_history.views import MissingHistoryRecordsField

logger = logging.getLogger()

from .utils import get_grupo_assinante_backend, get_grupo_assinante_model_str

BackendGrupoAssinante = get_grupo_assinante_backend()


class NaoPodeAssinarException(Exception):
    message = 'Usuario nao pode assinar'


class GrupoNaoPodeAssinarException(NaoPodeAssinarException):
    message = 'Grupo nao e assintante deste documento'


class ExitemAssinaturasPendentes(Exception):
    message = 'Impossivel finalizar documento com assinaturas pendentes'


class JaEstaAssinado(Exception):
    pass


@python_2_unicode_compatible
class TipoDocumento(models.Model):
    titulo = models.CharField(max_length=255, blank=True)
    descricao = models.TextField(max_length=255, blank=True)

    def __str__(self):
        return '{}'.format(self.descricao)


@python_2_unicode_compatible
class Assinatura(models.Model):
    def __str__(self):
        return 'pk: {}'.format(self.pk)

    # documento
    documento = models.ForeignKey('Documento', related_name='assinaturas')
    versao_documento = models.PositiveIntegerField(null=True)

    # Defensoria
    grupo_assinante = models.ForeignKey(to=get_grupo_assinante_model_str(),
                                        related_name="%(app_label)s_%(class)s_assinaturas",
                                        )

    nome_defensoria = models.CharField(max_length=255, blank=True)

    # Usuario Assinante
    assinado_por = models.ForeignKey(to='auth.User',
                                     related_name="%(app_label)s_%(class)s_assinaturas",
                                     null=True)

    assinado_nome = models.CharField(max_length=255, blank=True)

    #  dados apos assinado
    assinado_em = models.DateTimeField(null=True, blank=True)
    hash_assinatura = models.TextField(blank=True)

    esta_assinado = models.BooleanField(default=False)

    #
    ativo = models.BooleanField(default=True)

    # auditoria
    cadastrado_por = models.ForeignKey(to='auth.User',
                                       related_name="%(app_label)s_%(class)s_cadastrado_por",
                                       editable=False)
    data_cadastro = models.DateTimeField(auto_now_add=True, editable=False)
    nome_cadastrado_por = models.CharField(max_length=255, blank=True)

    excluido_por = models.ForeignKey(to='auth.User',
                                     related_name="%(app_label)s_%(class)s_excluido_por",
                                     null=True)
    nome_excluido_por = models.CharField(max_length=255, blank=True)
    data_exclusao = models.DateTimeField(null=True)

    def pode_assinar(self, grupo_assinante, usuario_assinante, agora):
        return BackendGrupoAssinante.pode_assinar(
            document=self.documento,
            grupo_assinante=grupo_assinante,
            usuario=usuario_assinante,
            now_datetime=agora
        )

    def assinar(self, usuario_assinante):
        assert self.ativo == True, 'O registro nao esta ativo para ser assinado'

        assert self.esta_assinado == False, 'O registro ja esta assinado'

        agora = datetime.now()

        #

        #
        # se o usuario realmente estiver vinculado a esta defensoria, entao ele pode assinar
        if not self.pode_assinar(grupo_assinante=self.grupo_assinante,
                                 usuario_assinante=usuario_assinante,
                                 agora=agora):
            raise NaoPodeAssinarException()

        self.assinado_por = usuario_assinante
        self.assinado_em = agora
        self.assinado_nome = self.assinado_por.get_full_name()
        self.versao_documento = self.documento.versao_numero
        self.esta_assinado = True
        self.hash_assinatura = self.gerar_hash()
        self.save()

    def gerar_hash(self, ):
        print("Assinatura: {} - self.documento.versao_numero: {}".format(self.pk, self.documento.versao_numero))

        para_hash = '{username}-{conteudo}-{versao}-{assinado_em}'.format(  # username=self.assinado_por.username,
            username=self.assinado_por.username,
            conteudo=self.documento.conteudo,
            versao=self.documento.versao_numero,
            assinado_em=self.assinado_em.strftime("%Y-%m-%d %H:%M:%S.%f")
        )
        password_hasher = SHA1PasswordHasher()
        assinatura_hash = password_hasher.encode(para_hash, 'djdocumentos')

        return assinatura_hash

    def revogar(self, usuario_atual):
        self.ativo = False
        self.excluido_por = usuario_atual
        self.nome_excluido_por = usuario_atual.get_full_name()
        self.data_exclusao = datetime.now()
        self.save()

    def save(self, *args, **kwargs):
        # pre save

        if self.grupo_assinante:
            if not self.pk:
                self.nome_defensoria = self.grupo_assinante.name
        if self.cadastrado_por:
            if not self.pk:
                self.nome_cadastrado_por = self.cadastrado_por.get_full_name()
        super(Assinatura, self).save(args, kwargs)
        # post save


# Create your models here.
class Documento(models.Model):
    uuid_hash = models.UUIDField(editable=False, unique=True, null=True, db_index=True)

    def __unicode__(self):
        return 'pk: {}'.format(self.pk)

    assunto = models.CharField(max_length=255, blank=True)

    cabecalho = models.TextField(blank=True)
    titulo = models.TextField(blank=True)
    conteudo = models.TextField(blank=True)
    rodape = models.TextField(blank=True)

    # template
    eh_template = models.BooleanField(default=False, editable=True)
    template_descricao = models.TextField(blank=True)
    # end template

    assinatura_hash = models.TextField(blank=True, editable=False, unique=True, null=True)

    data_assinado = models.DateTimeField(null=True)
    esta_assinado = models.BooleanField(default=False, editable=True)

    esta_pronto_para_assinar = models.BooleanField(default=False, editable=True)

    grupos_assinates = models.ManyToManyField(to=get_grupo_assinante_model_str(),
                                              through='Assinatura',
                                              )

    versao_numero = models.PositiveIntegerField(default=1, auto_created=True, editable=False)
    tipo_documento = models.ForeignKey(TipoDocumento, null=True, on_delete=models.SET_NULL,
                                       verbose_name='Tipo do Documento')

    # auditoria
    criado_por = models.ForeignKey(to='auth.User',
                                   related_name="%(app_label)s_%(class)s_criado_por", null=True,
                                   blank=True, on_delete=models.SET_NULL, editable=False)
    criado_por_nome = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True, editable=False)

    modificado_por = models.ForeignKey(to='auth.User', null=True,
                                       blank=True, on_delete=models.SET_NULL, editable=False)
    modificado_em = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False)

    modificado_por_nome = models.CharField(max_length=255, blank=True)

    esta_ativo = models.NullBooleanField(default=True, editable=False)

    versoes = HistoricalRecords()

    def pode_editar(self, usuario_atual):
        # TODO: Verificar ManyToManyField de Defensoria para Documento, com related donos
        return BackendGrupoAssinante.pode_editar(document=self,
                                                 usuario=usuario_atual)

    def pode_visualizar(self, usuario_atual):
        if self.pode_editar(usuario_atual):
            return True
        else:
            return BackendGrupoAssinante.pode_visualizar(
                document=self,
                usuario=usuario_atual
            )

    def adicionar_grupos_assinantes(self, defensorias_assinantes, cadastrado_por):
        for defensoria in defensorias_assinantes:
            assinatura = self.grupos_assinates.through(
                documento=self,
                grupo_assinante=defensoria,
                cadastrado_por=cadastrado_por
            )
            assinatura.save()

    def revogar_assinaturas(self, usuario_atual):
        assinaturas = self.assinaturas.filter(ativo=True, esta_assinado=True)
        for assinatura in assinaturas:
            assinatura.revogar(usuario_atual=usuario_atual)
            self.adicionar_grupos_assinantes(
                defensorias_assinantes=(assinatura.defensoria,),
                cadastrado_por=usuario_atual
            )

    def assinar(self, grupo_assinante, usuario_assinante):
        try:
            assinatura = self.assinaturas.get(
                grupo_assinante=grupo_assinante,
                ativo=True,
            )
            if assinatura.esta_assinado:
                raise JaEstaAssinado()
            if assinatura:
                try:
                    assinatura.assinar(usuario_assinante=usuario_assinante)
                except NaoPodeAssinarException as e:
                    logger.error(e)
                    raise e
                except AssertionError as e:
                    logger.error(e)
                    raise e

                    #
        except self.grupos_assinates.through.DoesNotExist as e:
            logger.error(e)
            raise GrupoNaoPodeAssinarException()

    def finalizar_documento(self, usuario):
        if self.assinaturas.filter(ativo=True, esta_assinado=False).exists():
            raise ExitemAssinaturasPendentes()
        self.assinatura_hash = self.gerar_hash()
        self.data_assinado = datetime.now()
        self.esta_assinado = True

        self.save()

    def gerar_hash(self):
        hashes = self.assinaturas.filter(ativo=True).values_list('hash_assinatura', flat=True)

        return 'Balackbah'

    def save(self, *args, **kwargs):

        if self.pk:
            if hasattr(self._meta, 'simple_history_manager_attribute'):
                history_manager = getattr(self, self._meta.simple_history_manager_attribute)
                max_db_value = list(history_manager.aggregate(Max('versao_numero')).values())[0]
                self.versao_numero = max_db_value + 1 if max_db_value >= self.versao_numero else self.versao_numero + 1
            else:
                raise MissingHistoryRecordsField(
                    "The model %(cls)s does not have a HistoryRecords field. Define a HistoryRecords()"
                    " field into %(cls)s model class."
                    "\neg.:"
                    "\nhistory = HistoryRecords()"
                    "\n\nafter do this, run:"
                    "\npython manage.py makemigrations %(app_label)s"
                    "\npython manage.py migrate %(app_label)s"
                    "\npython manage.py populate_history %(app_label)s.%(cls)s " % {
                        'app_label': self._meta.app_label,
                        'cls': self.__class__.__name__
                    })
        if not self.esta_assinado:
            self.assinatura_hash = None
        super(Documento, self).save(*args, **kwargs)
