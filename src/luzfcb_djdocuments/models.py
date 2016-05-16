# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.contrib.auth.hashers import SHA1PasswordHasher
from django.db import models, transaction
from django.db.models import Max
from django.utils import timezone
from django.utils.six import python_2_unicode_compatible
from simple_history.models import HistoricalRecords
from simple_history.views import MissingHistoryRecordsField

from .settings import USER_MODEL
from .utils import identificador


class DocumentoQuerySet(models.QuerySet):

    def ativos(self):
        return self.filter(esta_ativo=True)

    def inativos(self):
        return self.filter(esta_ativo=False)

    def assinados(self):
        return self.filter(esta_assinado=True, esta_ativo=True)


class DocumentoManager(models.Manager):

    def get_queryset(self):
        return DocumentoQuerySet(model=self.model, using=self._db).ativos().filter(eh_template=False)


class DocumentoAdminManager(models.Manager):

    def get_queryset(self):
        return DocumentoQuerySet(model=self.model, using=self._db)


class AssinaturaQuerySet(models.QuerySet):

    def inativos(self):
        return self.filter(esta_ativo=False)

    def ativos(self):
        return self.filter(esta_ativo=True)

    def nao_assinados(self, assinante=None):
        if assinante:
            return self.ativos().filter(esta_assinado=False, assinado_por=assinante)
        return self.ativos().filter(esta_assinado=False)

    def assinados(self, assinante=None):
        if assinante:
            return self.ativos().filter(esta_assinado=True, assinado_por=assinante)
        return self.ativos().filter(esta_assinado=True)


class AssinaturaManager(models.Manager):

    def get_queryset(self):
        return AssinaturaQuerySet(model=self.model, using=self._db).ativos()


class AssinaturaAdminManager(models.Manager):

    def get_queryset(self):
        return AssinaturaQuerySet(model=self.model, using=self._db)


@python_2_unicode_compatible
class TipoDocumento(models.Model):
    titulo = models.CharField(max_length=255, blank=True)
    descricao = models.TextField(max_length=255, blank=True)

    def __str__(self):
        return '{}'.format(self.descricao)


class Assinatura(models.Model):
    documento = models.ForeignKey(to='Documento',
                                  related_name="assinaturas",
                                  null=True,
                                  blank=True,
                                  on_delete=models.SET_NULL,
                                  editable=False,
                                  )

    assinado_por = models.ForeignKey(to=USER_MODEL,
                                     related_name="%(app_label)s_%(class)s_assinado_por",
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL,
                                     editable=False
                                     )

    # criado_em = models.DateTimeField(default=timezone.now, blank=True, editable=False)
    assinado_em = models.DateTimeField(blank=True, null=True, editable=False)
    versao_numero = models.IntegerField(editable=False, null=True)
    assinatura_hash = models.TextField(blank=True, editable=False, unique=True, null=True)
    # assinatura_salto = models.TextField(blank=True, editable=False, unique=True, null=True)

    esta_assinado = models.BooleanField(default=False, editable=True)
    esta_ativo = models.NullBooleanField(default=True, editable=True)

    modificado_em = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False)
    modificado_por = models.ForeignKey(to=USER_MODEL, null=True,
                                       blank=True, on_delete=models.SET_NULL, editable=False)

    objects = AssinaturaManager()
    admin_objects = AssinaturaAdminManager()

    class Meta:
        unique_together = ('documento', 'assinado_por', 'versao_numero')

    def __str__(self):
        return 'pk: {} - versao_numero: {} - (doc: {}  - ver: {}) - esta_ativo: {} - esta_assinado: {}'.format(self.pk,
                                                                                                               self.versao_numero,
                                                                                                               self.documento_id,
                                                                                                               self.documento.versao_numero,
                                                                                                               self.esta_ativo,
                                                                                                               self.esta_assinado
                                                                                                               )

    def save(self, *args, **kwargs):
        if self.documento and not self.versao_numero:
            self.versao_numero = self.documento.versao_numero

        super(Assinatura, self).save(*args, **kwargs)

    def assinar_documento(self, password=None):
        # if current_logged_user:
        #     self.assinado_por = current_logged_user
        try:
            self.assinado_em = timezone.now()
            self.esta_assinado = True
            # self.assinatura_salto = get_random_string(length=8, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

            para_hash = '{username}-{conteudo}-{versao}-{assinado_em}'.format(  # username=self.assinado_por.username,
                username=self.assinado_por.username,
                conteudo=self.documento.conteudo,
                versao=self.versao_numero + 1,
                assinado_em=self.assinado_em.strftime("%Y-%m-%d %H:%M:%S.%f")
            )
            password_hasher = SHA1PasswordHasher()
            self.assinatura_hash = password_hasher.encode(para_hash, 'djdocumentos')
            # self.assinatura_hash = password_hasher.encode(para_hash, self.assinatura_salto)
        except Exception as e:

            print('deu pau aqui: ', e)
        self.save()

    def remover_assinatura(self, password=None):
        # if current_logged_user:
        #     self.assinado_por = current_logged_user
        try:
            self.assinado_em = timezone.now()
            self.esta_assinado = True
            # self.assinatura_salto = get_random_string(length=8, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

            para_hash = '{username}-{conteudo}-{versao}-{assinado_em}'.format(  # username=self.assinado_por.username,
                username=self.assinado_por.username,
                conteudo=self.documento.conteudo,
                versao=self.versao_numero + 1,
                assinado_em=self.assinado_em.strftime("%Y-%m-%d %H:%M:%S.%f")
            )
            password_hasher = SHA1PasswordHasher()
            self.assinatura_hash = password_hasher.encode(para_hash, 'djdocumentos')
            # self.assinatura_hash = password_hasher.encode(para_hash, self.assinatura_salto)
        except Exception as e:

            print('deu pau aqui: ', e)
        self.save()


@python_2_unicode_compatible
class Documento(models.Model):
    assunto = models.CharField(max_length=255, blank=True)
    assinantes = models.ManyToManyField(to=USER_MODEL,
                                        related_name="%(app_label)s_%(class)s_assinantes",
                                        blank=True,
                                        editable=False,
                                        through='Assinatura',
                                        through_fields=('documento', 'assinado_por')
                                        )

    cabecalho = models.TextField(blank=True)
    titulo = models.TextField(blank=True)
    conteudo = models.TextField(blank=True)
    rodape = models.TextField(blank=True)

    eh_template = models.BooleanField(default=False, editable=True)
    template_descricao = models.TextField(blank=True)

    versao_numero = models.IntegerField(default=1, auto_created=True, editable=False)

    # tipo_documento = models.CharField(max_length=255, blank=True)
    tipo_documento = models.ForeignKey(TipoDocumento, null=True, on_delete=models.SET_NULL,
                                       verbose_name='Tipo do Documento')
    # tipo_documento_descricao = models.TextField(blank=True)

    # modelo_documento = models.ForeignKey('self',
    #                                      related_name='%(class)s_documentos',
    #                                      null=True,
    #                                      blank=True,
    #                                      on_delete=models.SET_NULL,
    #                                      limit_choices_to={'eh_template': True})

    # fields para auditoria
    criado_em = models.DateTimeField(default=timezone.now, blank=True, editable=False)
    criado_por = models.ForeignKey(to=USER_MODEL,
                                   related_name="%(app_label)s_%(class)s_criado_por", null=True,
                                   blank=True, on_delete=models.SET_NULL, editable=False)

    modificado_em = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False)
    modificado_por = models.ForeignKey(to=USER_MODEL,
                                       related_name="%(app_label)s_%(class)s_modificado_por", null=True,
                                       blank=True, on_delete=models.SET_NULL, editable=False)

    revertido_em = models.DateTimeField(blank=True, null=True, editable=False)
    revertido_por = models.ForeignKey(to=USER_MODEL,
                                      related_name="%(app_label)s_%(class)s_revertido_por", null=True,
                                      blank=True, on_delete=models.SET_NULL, editable=False)
    revertido_da_versao = models.IntegerField(null=True, default=None, auto_created=True, editable=False, blank=True)

    esta_ativo = models.NullBooleanField(default=True, editable=False)

    esta_bloqueado = models.NullBooleanField(default=False, editable=False)
    bloqueado_em = models.DateTimeField(blank=True, null=True, editable=False)
    bloqueado_por = models.ForeignKey(to=USER_MODEL,
                                      related_name="%(app_label)s_%(class)s_bloqueado_por", null=True,
                                      blank=True, on_delete=models.SET_NULL, editable=False)

    assinatura_hash = models.TextField(blank=True, editable=False, unique=True, null=True)
    # assinatura_salto = models.TextField(blank=True, editable=False, unique=True, null=True)

    esta_assinado = models.BooleanField(default=False, editable=True)
    # esta_assinatura_pendente = models.NullBooleanField(default=None, editable=True)

    assinado_em = models.DateTimeField(blank=True, null=True, editable=False)
    assinado_por = models.ForeignKey(to=USER_MODEL,
                                     related_name="%(app_label)s_%(class)s_assinado_por",
                                     null=True,
                                     blank=True, on_delete=models.SET_NULL, editable=False)

    assinatura_removida_em = models.DateTimeField(blank=True, null=True, editable=False)
    assinatura_removida_por = models.ForeignKey(to=USER_MODEL,
                                                related_name="%(app_label)s_%(class)s_assinatura_removida_por",
                                                null=True,
                                                blank=True, on_delete=models.SET_NULL, editable=False)

    versoes = HistoricalRecords()
    objects = DocumentoManager()
    admin_objects = DocumentoAdminManager()

    @property
    def assinatura_hash_upper_limpo(self):
        if self.assinatura_hash:
            return self.assinatura_hash.upper().split('$')[-1]
        return None

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
        if self.assinado_por:
            print(self.assinado_por.pk, ':', self.assinado_por.get_full_name())
        super(Documento, self).save(*args, **kwargs)

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

    def __str__(self):
        return '{}-{}-{}'.format(self.pk, self.versao_numero, getattr(self, 'esta_assinado', ''))

    def assinar_documento(self, assinado_por, current_logged_user, *args, **kwargs):
        # if current_logged_user:
        #     self.assinado_por = current_logged_user
        try:
            self.assinado_por = assinado_por
            self.assinado_em = timezone.now()
            self.esta_assinado = True
            self.modificado_por = current_logged_user
            # self.assinatura_salto = get_random_string(length=8, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

            para_hash = '{username}-{conteudo}-{versao}-{assinado_em}'.format(  # username=self.assinado_por.username,
                username=self.criado_por.username,
                conteudo=self.conteudo,
                versao=self.versao_numero,
                assinado_em=self.assinado_em.strftime("%Y-%m-%d %H:%M:%S.%f")
                # assinado_em=self.assinado_em
            )
            password_hasher = SHA1PasswordHasher()
            self.assinatura_hash = password_hasher.encode(para_hash, 'djdocumentos')
            # self.assinatura_hash = password_hasher.encode(para_hash, self.assinatura_salto)
        except Exception as e:

            print('deu pau aqui: ', e)
        self.save(*args, **kwargs)

    def remover_assinatura_documento(self, assinatura_removida_por, current_logged_user, *args, **kwargs):
        # if current_logged_user:
        #     self.assinatura_removida_por = current_logged_user
        self.assinatura_removida_em = timezone.now()
        self.assinatura_removida_por = assinatura_removida_por
        self.modificado_por = current_logged_user
        self.esta_assinado = False
        self.assinado_em = None
        self.assinado_por = None
        self.assinatura_hash = None
        # self.assinatura_salto = None
        self.save(*args, **kwargs)

        with transaction.atomic:
            for assinatura in self.assinaturas.select_for_update():
                assinatura.esta_ativo = False
                assinatura.save(update_fields=['esta_ativo'])

    class Meta:
        ordering = ['criado_em']
        verbose_name = 'Documento Digital'
        verbose_name_plural = 'Documentos Digitais'

        permissions = (
            ("pode_criar_documento", "Pode Criar documento"),
            ("pode_editar_documento", "Pode Editar documento"),
            ("pode_assinar_documento", "Pode Assinar documento"),
            ("pode_desativar_documento", "Pode Desativar documento"),
            ("pode_visualizar_versoes_anteriores_documento", "Pode Visualizar versoes anteriores de documento"),
            ("pode_reverter_para_uma_versao_anterior_documento", "Pode Reverter documento para uma versão anterior"),
            ("pode_imprimir", "Pode Imprimir documento"),
        )

# class DocumentoTemplateManager(models.Manager):
#     def get_queryset(self):
#         return super(DocumentoTemplateManager, self).get_queryset().filter(esta_ativo=True, eh_template=True)
#
#
# class DocumentoTemplate(Documento):
#     objects = DocumentoTemplateManager()
#
#     class Meta:
#         proxy = True
