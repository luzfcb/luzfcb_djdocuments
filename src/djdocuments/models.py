# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import logging
import uuid
from collections import Iterable, OrderedDict

from django.conf import settings
from django.contrib.auth.hashers import SHA1PasswordHasher, check_password
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Max, Q
from django.utils import timezone, six
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from simple_history.models import HistoricalRecords
from simple_history.views import MissingHistoryRecordsField
from model_utils import FieldTracker
from model_utils.models import SoftDeletableModel
from . import managers
from .utils import identificador, get_djdocuments_backend, get_grupo_assinante_model_str

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


# class Assinatura(SoftDeletableModel):
@python_2_unicode_compatible
class Assinatura(models.Model):
    def __str__(self):
        nome = self.assinado_por.get_full_name() if self.assinado_por else False
        nome_assinante = '{} (pk: {})'.format(nome, self.assinado_por_id) if nome else None
        return '<%(cls)s "%(atribs)s">' % {
            'cls': self.__class__.__name__,
            'atribs': OrderedDict({
                'pk': self.pk,
                'grupo_assinante': self.grupo_assinante_id,
                'nome_assinante': nome_assinante,
                'esta_assinado': self.esta_assinado,
                'ativo': self.ativo
            })
        }

    # documento
    documento = models.ForeignKey('Documento', related_name='assinaturas')
    documento_pk_uuid = models.UUIDField(editable=False, null=True, db_index=True)
    documento_identificador_versao = models.CharField(editable=False, max_length=25, blank=True)
    documento_assunto = models.CharField(editable=False, max_length=255, blank=True)

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
    nome_cadastrado_por = models.CharField(max_length=255, blank=True, editable=False)

    excluido_por = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                     related_name="%(app_label)s_%(class)s_excluido_por",
                                     null=True, blank=True, editable=False)
    nome_excluido_por = models.CharField(max_length=255, blank=True, default='')
    data_exclusao = models.DateTimeField(null=True, blank=True, editable=False)

    objects = managers.AssinaturaManager()
    tracker = FieldTracker()

    def get_absolute_url(self):
        return self.get_url_para_assinar

    @property
    def get_preview_url(self):
        return reverse('documentos:validar-detail', kwargs={'slug': self.documento_pk_uuid})

    @property
    def get_url_para_assinar(self):
        url = None
        if not self.esta_assinado:
            if self.assinado_por:
                url = reverse('documentos:assinar_por_grupo_por_usuario',
                              kwargs={
                                  'slug': self.documento_pk_uuid,
                                  'user_id': self.assinado_por_id,
                                  'group_id': self.grupo_assinante_id
                              })
            else:
                url = reverse('documentos:assinar_por_grupo',
                              kwargs={
                                  'slug': self.documento_pk_uuid,
                                  'group_id': self.grupo_assinante_id
                              })
        return url

    @property
    def get_url_para_assinar_e_finalizar(self):
        url = None
        if not self.esta_assinado:
            if self.assinado_por:
                url = reverse('documentos:assinar_finalizar_por_grupo_por_usuario',
                              kwargs={
                                  'slug': self.documento_pk_uuid,
                                  'user_id': self.assinado_por_id,
                                  'group_id': self.grupo_assinante_id
                              })
            else:
                url = reverse('documentos:assinar_finalizar_por_grupo',
                              kwargs={
                                  'slug': self.documento_pk_uuid,
                                  'group_id': self.grupo_assinante_id
                              })
        return url

    @property
    def get_url_para_remover(self):
        url = None
        if not self.esta_assinado:
            url = reverse('documentos:remover_assinatura',
                          kwargs={
                              'document_slug': self.documento_pk_uuid,
                              'pk': self.pk
                          })
        return url

    @property
    def get_assunto(self):
        return self.documento_assunto

    @property
    def identificador_versao(self):
        return self.documento_identificador_versao

    def pode_assinar(self, grupo_assinante, usuario_assinante):
        return DjDocumentsBackend.pode_assinar(
            document=self.documento,
            grupo_assinante=grupo_assinante,
            usuario=usuario_assinante,
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
                                 usuario_assinante=usuario_assinante):
            raise NaoPodeAssinarException('Usuario não pode assinar esse documento')
        if self.assinado_por:
            if not self.assinado_por == usuario_assinante:
                raise NaoPodeAssinarException('Usuario não pode assinar esse documento')

        self.assinado_por = usuario_assinante
        self.assinado_em = agora
        self.assinado_nome = self.assinado_por.get_full_name()
        self.versao_documento = self.documento.versao_numero
        self.esta_assinado = True
        self.hash_assinatura = self.gerar_hash()
        self.save()

    def gerar_hash(self, ):

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
        if not self.assinado_nome and self.assinado_por:
            self.assinado_nome = self.assinado_por.get_full_name()
        if not self.documento_pk_uuid and self.documento:
            self.documento_pk_uuid = self.documento.pk_uuid
        if not self.documento_assunto and self.documento:
            self.documento_assunto = self.documento.assunto
        if not self.documento_identificador_versao and self.documento:
            self.documento_identificador_versao = self.documento.identificador_versao
        super(Assinatura, self).save(*args, **kwargs)
        # post save


@python_2_unicode_compatible
class Documento(SoftDeletableModel):
    pk_uuid = models.UUIDField(editable=False, unique=True, null=True, db_index=True, default=uuid.uuid4)

    def __unicode__(self):
        return 'pk: {}'.format(self.pk)

    assunto = models.CharField(max_length=255, blank=True)

    cabecalho = models.TextField(blank=True, default='')
    # titulo = models.TextField(blank=True, default='')
    conteudo = models.TextField(blank=True, default='')
    rodape = models.TextField(blank=True, default='')

    # template
    eh_modelo = models.BooleanField(default=False, editable=True)
    eh_modelo_padrao = models.BooleanField(default=False, editable=True)
    modelo_descricao = models.TextField(blank=True, default='')
    modelo_pronto_para_utilizacao = models.BooleanField(default=False)
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
    # grupo_dono_nome = models.CharField(max_length=500, blank=True, editable=False)

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

    excluido_por = models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True,
                                     related_name="%(app_label)s_%(class)s_excluido_por",
                                     blank=True, on_delete=models.SET_NULL, editable=False)
    excluido_em = models.DateTimeField(null=True, editable=False)

    excluido_por_nome = models.CharField(max_length=255, blank=True, default='', editable=False)

    esta_ativo = models.NullBooleanField(default=True, editable=False)

    # pdf
    page_margin_top = models.FloatField(help_text='Margem superior em relação a pagina', default=41.5, blank=True,
                                        null=True)
    page_margin_bottom = models.FloatField(help_text='Margem inferior em relação a pagina', default=35.5, blank=True,
                                           null=True)
    page_margin_left = models.FloatField(help_text='Margem esquerda em relação a pagina', default=1.0, blank=True,
                                         null=True)
    page_margin_right = models.FloatField(help_text='Margem direita em relação a pagina', default=4.0, blank=True,
                                          null=True)

    versoes = HistoricalRecords()
    tracker = FieldTracker()
    objects = managers.DocumentoManager()
    admin_objects = managers.DocumentoAdminManager()

    def __str__(self):

        nome = getattr(self.grupo_dono, DjDocumentsBackend.group_name_atrib) if self.grupo_dono_id else False
        nome_grupo_dono = '{}(pk: {})'.format(nome, self.grupo_dono_id) if nome else None
        return '<%(cls)s "%(atribs)s">' % {
            'cls': self.__class__.__name__,
            'atribs': OrderedDict({
                'pk': self.pk,
                'pk_uuid': six.text_type(self.pk_uuid),
                'eh_modelo': self.eh_modelo,
                'grupo_dono': nome_grupo_dono,
                'esta_ativo': self.esta_ativo
            })
        }

    @property
    def estado_documental_str(self):
        if self.possui_assinatura_pendente == 0:
            msg = 'Ainda não possui assinantes cadastrados'
        elif self.possui_assinatura_pendente == 1:
            msg = 'Possui assinaturas pendentes'
        elif self.pronto_para_finalizar:
            msg = 'Pronto para Finalizar'
        else:
            msg = 'Assinado e Finalizado'

        return msg

    @cached_property
    def assinates_nomes(self):
        assinantes = self.assinaturas.filter(~models.Q(assinado_por=None)).order_by('grupo_assinante_nome').values_list(
            'assinado_nome', 'grupo_assinante_nome',
        )
        a = assinantes
        return a

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
        """
        Retorna pk + versao incluindo zeros, no formato 00000000v000. Ex:

        :return:
        """
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

    def pode_excluir_documento(self, usuario_atual):
        return DjDocumentsBackend.pode_excluir_documento(document=self,
                                                         usuario=usuario_atual)

    def pode_visualizar(self, usuario_atual):
        if self.pode_editar(usuario_atual):
            return True
        else:
            return DjDocumentsBackend.pode_visualizar(
                document=self,
                usuario=usuario_atual
            )

    def adicionar_pendencia_de_assinatura_por_usuario(self, grupo, assinado_por, cadastrado_por):
        # se usuario esta no grupo
        if grupo.pk in [d.pk for d in DjDocumentsBackend.get_grupos_usuario(assinado_por)]:
            # se usuario nao possui assinatura pendente
            if not self.grupos_assinates.through.objects.filter(documento=self, assinado_por=assinado_por,
                                                                grupo_assinante=grupo, ativo=True).exists():
                # entao, incluir pendencia de assinatura
                assinatura = None
                try:
                    # verificar se existe assinatura pendente para o grupo, sem usuario
                    assinatura = self.grupos_assinates.through.objects.get(documento=self, assinado_por=None,
                                                                           grupo_assinante=grupo, ativo=True)
                    assinatura.assinado_por = assinado_por
                    assinatura.cadastrado_por = cadastrado_por
                except self.grupos_assinates.through.DoesNotExist:

                    assinatura = self.grupos_assinates.through(documento=self,
                                                               grupo_assinante=grupo,
                                                               assinado_por=assinado_por,
                                                               cadastrado_por=cadastrado_por)
                finally:
                    assinatura.save()
                    return True
        return False

    def adicionar_grupos_assinantes(self, grupos_assinantes, cadastrado_por):
        if not isinstance(grupos_assinantes, Iterable):
            grupos_assinantes = [grupos_assinantes]
        for grupo in grupos_assinantes:
            if not self.grupos_assinates.through.objects.filter(documento=self, grupo_assinante=grupo).exists():
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

        assinatura = self.assinaturas.filter(
            Q(grupo_assinante=grupo_assinante) &
            Q(ativo=True) & (
                Q(assinado_por=None) | Q(assinado_por=usuario_assinante)
            )
        ).first()

        if assinatura:
            if assinatura.esta_assinado:
                raise JaEstaAssinado('Documento já esta assinado')
            try:
                assinatura.assinar(usuario_assinante=usuario_assinante, senha=senha)
            except NaoPodeAssinarException as e:
                logger.error(e)
                raise e
            except AssertionError as e:
                logger.error(e)
                raise e
            return assinatura
        else:
            raise NaoPodeAssinarException('Usuario não pode assinar esse documento')

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
    def possui_assinatura_assinada(self):
        return self.assinaturas.filter(ativo=True, esta_assinado=True).exists()

    @cached_property
    def pronto_para_finalizar(self):
        if self.possui_assinatura_pendente < 0 and not self.esta_assinado:
            return True
        return False

    @property
    def esta_assinado_e_finalizado(self):
        if self.esta_assinado and self.assinatura_hash and self.possui_assinatura_assinada and self.possui_assinatura_pendente == -1:
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

    def get_absolute_url(self):
        if self.eh_modelo:
            url = reverse('documentos:validar-detail-modelo', kwargs={'slug': self.pk_uuid})
        else:
            url = reverse('documentos:validar-detail', kwargs={'slug': self.pk_uuid})
        return url

    @property
    def get_preview_url(self):
        if self.eh_modelo:
            url = reverse('documentos:validar-detail-modelo', kwargs={'slug': self.pk_uuid})
        else:
            url = reverse('documentos:validar-detail', kwargs={'slug': self.pk_uuid})
        return url

    @property
    def get_pdf_url(self):
        if self.eh_modelo:
            url = reverse('documentos:validar-detail-modelo-pdf', kwargs={'slug': self.pk_uuid})
        else:
            url = reverse('documentos:validar_detail_pdf', kwargs={'slug': self.pk_uuid})
        return url

    @property
    def get_edit_url(self):
        if self.eh_modelo:
            url = reverse('documentos:editar-modelo', kwargs={'slug': self.pk_uuid})
        else:
            url = reverse('documentos:editar', kwargs={'slug': self.pk_uuid})

        return url

    @property
    def get_adicionar_assinante_url(self):
        url = '#'
        if not self.eh_modelo:
            url = reverse('documentos:adicionar_assinantes', kwargs={'slug': self.pk_uuid})
        return url

    @property
    def get_finalizar_url(self):
        url = '#'
        if not self.eh_modelo:
            url = reverse('documentos:finalizar_assinatura', kwargs={'slug': self.pk_uuid})
        return url

    _desabilitar_temporiariamente_versao_numero = False

    def save(self, *args, **kwargs):
        if not self.pk_uuid:
            self.pk_uuid = uuid.uuid4()
        if self.pk:
            if hasattr(self._meta, 'simple_history_manager_attribute'):
                if not self._desabilitar_temporiariamente_versao_numero:
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
        if not self.criado_por_nome and self.criado_por:
            self.criado_por_nome = self.criado_por.get_full_name()

        if not self.esta_assinado:
            self.assinatura_hash = None

        assinatura_update_dict = {}
        # atualiza assunto das assinaturas vinculadas a este documento
        if self.pk and self.tracker.has_changed('assunto'):
            assinatura_update_dict['documento_assunto'] = self.assunto

        if self.pk and self.tracker.has_changed('versao_numero'):
            assinatura_update_dict['documento_identificador_versao'] = self.identificador_versao

        update_fields = None
        if self.pk and not hasattr(self, '_generated_by_simple_history'):
            update_fields = kwargs.pop('update_fields', [])
            update_fields.extend(list(self.tracker.changed().keys()))
            update_fields = list(set(update_fields))

        super(Documento, self).save(update_fields=update_fields, *args, **kwargs)

        if self.pk and assinatura_update_dict:
            self.assinaturas.update(**assinatura_update_dict)

    def delete(self, using=None, soft=True, current_user=None, *args, **kwargs):
        self.excluido_em = timezone.now()
        if current_user and not isinstance(current_user, AnonymousUser):
            self.excluido_por = current_user
            self.excluido_por_nome = self.excluido_por.get_full_name()
        self._desabilitar_temporiariamente_versao_numero = True
        super(Documento, self).delete(using, soft, *args, **kwargs)
        self._desabilitar_temporiariamente_versao_numero = False


class PDFDocument(models.Model):
    file = models.FileField(upload_to='djdocuments')
    documento = models.OneToOneField('Documento', related_name='pdf')
    documento_pk_uuid = models.UUIDField(editable=False, null=True, db_index=True)
    documento_identificador_versao = models.CharField(editable=False, max_length=25, blank=True)

    def save(self, *args, **kwargs):
        if not self.documento_pk_uuid and self.documento:
            self.documento_pk_uuid = self.documento.pk_uuid
        if not self.documento_identificador_versao and self.documento:
            self.documento_identificador_versao = self.documento.identificador_versao
        super(PDFDocument, self).save(*args, **kwargs)
