# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import logging
import uuid
from collections import Iterable

from django.conf import settings
from django.contrib.auth.hashers import SHA1PasswordHasher, check_password
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from simple_history.models import HistoricalRecords
from simple_history.views import MissingHistoryRecordsField

from djdocuments.utils import identificador

from . import managers
from .utils import get_djdocuments_backend, get_grupo_assinante_model_str

logger = logging.getLogger()

DjDocumentsBackend = get_djdocuments_backend()

__all__ = (
    'Documento',
    'Assinatura',
    'TipoDocumento'
)


class NaoPodeAssinarException(ValidationError):
    message = 'Usuario nao pode assinar'


class GrupoNaoPodeAssinarException(ValidationError):
    message = 'Grupo nao e assintante deste documento'


class ExitemAssinaturasPendentes(ValidationError):
    message = 'Impossivel finalizar documento com assinaturas pendentes'


class JaEstaAssinado(ValidationError):
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
        return 'pk: {}, grupo_assinante: {}'.format(self.pk, self.grupo_assinante.pk)

    # documento
    documento = models.ForeignKey('Documento', related_name='assinaturas')
    versao_documento = models.PositiveIntegerField(null=True)

    # Defensoria
    grupo_assinante = models.ForeignKey(to=get_grupo_assinante_model_str(),
                                        related_name="%(app_label)s_%(class)s_assinaturas",
                                        )

    grupo_assinante_nome = models.CharField(max_length=255, blank=True)

    # Usuario Assinante
    assinado_por = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                     related_name="%(app_label)s_%(class)s_assinaturas",
                                     null=True)

    assinado_nome = models.CharField(max_length=255, blank=True)

    #  dados apos assinado
    assinado_em = models.DateTimeField(null=True, blank=True)
    hash_assinatura = models.TextField(blank=True)
    esta_assinado = models.BooleanField(default=False, editable=False)

    ativo = models.NullBooleanField(default=True, editable=False)

    # auditoria
    cadastrado_por = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                       related_name="%(app_label)s_%(class)s_cadastrado_por",
                                       editable=False)
    cadastrado_em = models.DateTimeField(auto_now_add=True, editable=False)
    nome_cadastrado_por = models.CharField(max_length=255, blank=True)

    excluido_por = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                     related_name="%(app_label)s_%(class)s_excluido_por",
                                     null=True, blank=True)
    nome_excluido_por = models.CharField(max_length=255, blank=True)
    data_exclusao = models.DateTimeField(null=True, blank=True)

    objects = managers.AssinaturaManager()

    def pode_assinar(self, grupo_assinante, usuario_assinante, agora):
        return DjDocumentsBackend.pode_assinar(
            document=self.documento,
            grupo_assinante=grupo_assinante,
            usuario=usuario_assinante,
            now_datetime=agora
        )

    def pode_remover_assinatura(self, usuario_atual):
        """
        Verifica se o usuario_atual pode remover esta assinatura
        :param usuario_atual:
        :return: (status:bool, mensagem:str)
        """
        return DjDocumentsBackend.pode_remover_assinatura(
            document=self.documento,
            assinatura=self,
            usuario_atual=usuario_atual
        )

    def assinar(self, usuario_assinante, senha):

        if not check_password(senha, usuario_assinante.password):
            raise ValidationError('Senha inválida para o usuario selecionado')

        assert self.ativo is True, 'O registro nao esta ativo para ser assinado'

        assert self.esta_assinado is False, 'O registro ja esta assinado'

        agora = timezone.now()

        #

        #
        # se o usuario realmente estiver vinculado a esta defensoria, entao ele pode assinar
        if not self.pode_assinar(grupo_assinante=self.grupo_assinante,
                                 usuario_assinante=usuario_assinante,
                                 agora=agora):
            raise NaoPodeAssinarException('Usuario não pode assinar esse documento')

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
        self.data_exclusao = timezone.now()
        self.save()

    def save(self, *args, **kwargs):
        # pre save

        if self.grupo_assinante and not self.grupo_assinante_nome:
            if not self.pk:
                backend = get_djdocuments_backend()
                self.grupo_assinante_nome = backend.get_grupo_name(self.grupo_assinante)
        if self.cadastrado_por:
            if not self.pk:
                self.cadastrado_em = timezone.now()
                self.nome_cadastrado_por = self.cadastrado_por.get_full_name()
        super(Assinatura, self).save(args, kwargs)
        # post save


# Create your models here.
class Documento(models.Model):
    pk_uuid = models.UUIDField(editable=False, unique=True, null=True, db_index=True, default=uuid.uuid4)

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

    data_assinado = models.DateTimeField(null=True, blank=True)
    esta_assinado = models.BooleanField(default=False, editable=False)

    esta_pronto_para_assinar = models.BooleanField(default=False, editable=True)

    grupos_assinates = models.ManyToManyField(to=get_grupo_assinante_model_str(),
                                              through='Assinatura',
                                              )
    # Defensoria
    grupo_dono = models.ForeignKey(to=get_grupo_assinante_model_str(),
                                   related_name="%(app_label)s_%(class)s_donos",
                                   null=True,
                                   blank=True,
                                   )
    versao_numero = models.PositiveIntegerField(default=1, auto_created=True, editable=False)
    tipo_documento = models.ForeignKey(TipoDocumento, null=True, on_delete=models.SET_NULL,
                                       verbose_name='Tipo do Documento')

    # auditoria
    criado_por = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                   related_name="%(app_label)s_%(class)s_criado_por", null=True,
                                   blank=True, on_delete=models.SET_NULL, editable=False)
    criado_por_nome = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True, editable=False)

    modificado_por = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True,
                                       blank=True, on_delete=models.SET_NULL, editable=False)
    modificado_em = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False)

    modificado_por_nome = models.CharField(max_length=255, blank=True)

    esta_ativo = models.NullBooleanField(default=True, editable=False)

    versoes = HistoricalRecords()
    objects = managers.DocumentoManager()
    admin_objects = managers.DocumentoAdminManager()

    @property
    def _history_user(self):
        return self.modificado_por

    @_history_user.setter
    def _history_user(self, value):
        self.modificado_por = value

    @property
    def identificador_documento(self):
        if not self.pk:
            return None
        return identificador.document_number(self.pk)

    @property
    def identificador_versao(self):
        if not self.pk:
            return None
        return identificador.document(self.pk, self.versao_numero)

    @property
    def document_number(self):
        if not self.pk:
            return None
        return identificador.document_number(self.pk)

    @property
    def document_version_number(self):
        if not self.pk:
            return None
        return identificador.document_version_number(self.versao_numero)

    def pode_editar(self, usuario_atual):
        # TODO: Verificar ManyToManyField de Defensoria para Documento, com related donos
        return DjDocumentsBackend.pode_editar(document=self,
                                              usuario=usuario_atual)

    def pode_visualizar(self, usuario_atual):
        if self.pode_editar(usuario_atual):
            return True
        else:
            return DjDocumentsBackend.pode_visualizar(
                document=self,
                usuario=usuario_atual
            )

    def adicionar_grupos_assinantes(self, grupos_assinantes, cadastrado_por):
        if not isinstance(grupos_assinantes, Iterable):
            grupos_assinantes = [grupos_assinantes]
        for grupo in grupos_assinantes:
            try:
                self.grupos_assinates.through.objects.get(documento=self, grupo_assinante=grupo)
            except self.grupos_assinates.through.DoesNotExist:
                obj = self.grupos_assinates.through(documento=self,
                                                    grupo_assinante=grupo,
                                                    cadastrado_por=cadastrado_por)
                obj.save()

    def remover_grupos_assinantes(self, grupos_assinantes, removido_por):
        if not isinstance(grupos_assinantes, Iterable):
            grupos_assinantes = [grupos_assinantes]
        grupos_assinantes_pk_list = [g.pk for g in grupos_assinantes if not g.assinado_por]
        for assinatura in self.assinaturas.filter(grupo_assinante__in=grupos_assinantes_pk_list, assinado_por=None):
            assinatura.revogar(usuario_atual=removido_por)

    def revogar_assinaturas(self, usuario_atual):
        assinaturas = self.assinaturas.filter(ativo=True, esta_assinado=True)
        for assinatura in assinaturas:
            assinatura.revogar(usuario_atual=usuario_atual)
            self.adicionar_grupos_assinantes(
                grupos_assinantes=(assinatura.defensoria,),
                cadastrado_por=usuario_atual
            )

    def assinar(self, grupo_assinante, usuario_assinante, senha, usuario_atual=None):
        try:
            assinatura = self.assinaturas.get(
                grupo_assinante=grupo_assinante,
                ativo=True,
            )
            if assinatura.esta_assinado:
                raise JaEstaAssinado('Documento já esta assinado')
            if assinatura:
                try:
                    assinatura.assinar(usuario_assinante=usuario_assinante, senha=senha)
                except NaoPodeAssinarException as e:
                    logger.error(e)
                    raise e
                except AssertionError as e:
                    logger.error(e)
                    raise e

            return assinatura
        except self.grupos_assinates.through.DoesNotExist as e:
            logger.error(e)
            raise GrupoNaoPodeAssinarException('GrupoNaoPodeAssinarException')

    @cached_property
    def possui_assinatura_pendente(self):
        """
        :return: -1
        """
        if not self.assinaturas.filter(ativo=True).exists():
            # ainda nao tem assinantes cadastrados
            return 0
        else:
            if self.assinaturas.filter(ativo=True, esta_assinado=False).exists():
                return 1
            else:
                # nao possui
                return -1

    @cached_property
    def pronto_para_finalizar(self):
        if self.possui_assinatura_pendente < 0 and not self.esta_assinado:
            return True
        return False

    @property
    def esta_finalizado(self):
        if not self.esta_assinado and not self.assinatura_hash:
            return False
        return True

    def finalizar_documento(self, usuario):
        if not self.pronto_para_finalizar:
            raise ExitemAssinaturasPendentes('Impossivel finalizar documento, ainda existem assinaturas pendentes')
        self.modificado_por = usuario
        self.modificado_por_nome = self.modificado_por.get_full_name()
        self.data_assinado = timezone.now()
        self.assinatura_hash = self.gerar_hash(self.data_assinado)
        self.esta_assinado = True

        self.save()

    def gerar_hash(self, data_assinado):
        hashes = self.assinaturas.filter(ativo=True).values_list('hash_assinatura', flat=True)
        para_hash = "&".join(hashes)
        para_hash = "{}-{}".format(data_assinado.strftime("%Y-%m-%d %H:%M:%S.%f"), para_hash)
        password_hasher = SHA1PasswordHasher()
        assinatura_hash = password_hasher.encode(para_hash, 'djdocumentos')

        return assinatura_hash

    @property
    def get_assinatura_hash_upper_limpo(self):
        if self.assinatura_hash:
            return self.assinatura_hash.upper().split('$')[-1]
        return None

    def save(self, *args, **kwargs):
        if not self.pk_uuid:
            self.pk_uuid = uuid.uuid4()
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
        if not self.criado_por_nome:
            if self.criado_por:
                self.criado_por_nome = self.criado_por.get_full_name()
        if not self.esta_assinado:
            self.assinatura_hash = None
        super(Documento, self).save(*args, **kwargs)
