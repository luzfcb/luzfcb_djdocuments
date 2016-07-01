# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

import logging
from datetime import datetime

from django.contrib.auth.hashers import SHA1PasswordHasher
from django.db import models
from django.db.models import Q, python_2_unicode_compatible
from simple_history.models import HistoricalRecords
from simple_history.views import MissingHistoryRecordsField

logger = logging.getLogger()


class NaoPodeAssinarException(Exception):
    message = 'Usuario nao pode assinar'


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
    grupos_de_assinante = models.ForeignKey(to='contrib.Defensoria',
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

    def pode_assinar(self, grupos_de_assinante, usuario_assinante, agora):
        defensorias = usuario_assinante.servidor.defensor.all_atuacoes.filter(
            Q(ativo=True) &
            Q(defensoria=grupos_de_assinante) &
            Q(data_inicial__lte=agora) &
            (
                Q(data_final__gte=agora) |
                Q(data_final=None)
            )
        ).count()
        return bool(defensorias)

    def assinar(self, usuario_assinante):
        assert self.ativo == True, 'O registro nao esta ativo para ser assinado'

        assert self.esta_assinado == False, 'O registro ja esta assinado'

        agora = datetime.now()

        #

        #
        # se o usuario realmente estiver vinculado a esta defensoria, entao ele pode assinar
        if not self.pode_assinar(grupos_de_assinante=self.grupos_de_assinante,
                                 usuario_assinante=usuario_assinante,
                                 agora=agora):
            raise NaoPodeAssinarException()

        self.assinado_por = usuario_assinante
        self.assinado_em = agora
        self.hash_assinatura = self.gerar_hash()
        self.assinado_nome = self.assinado_por.get_full_name()
        self.versao_documento = self.documento.versao_numero
        self.esta_assinado = True
        self.save()

    def gerar_hash(self, ):
        print("self.versao_numero: {} - self.documento.versao_numero: {}".format(self.versao_numero,
                                                                                 self.documento.versao_numero))

        para_hash = '{username}-{conteudo}-{versao}-{assinado_em}'.format(  # username=self.assinado_por.username,
            username=self.assinado_por.username,
            conteudo=self.documento.conteudo,
            versao=self.versao_numero,
            assinado_em=self.assinado_em.strftime("%Y-%m-%d %H:%M:%S.%f")
        )
        password_hasher = SHA1PasswordHasher()
        self.assinatura_hash = password_hasher.encode(para_hash, 'djdocumentos')

        return 'Bah'

    def revogar(self, usuario_atual):
        self.ativo = False
        self.excluido_por = usuario_atual
        self.nome_excluido_por = usuario_atual.get_full_name()
        self.data_exclusao = datetime.now()
        self.save()

    def save(self, *args, **kwargs):
        # pre save

        if self.grupos_de_assinante:
            if not self.pk:
                self.nome_defensoria = self.grupos_de_assinante.nome
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

    conteudo_documento = models.TextField(blank=True)

    hash_assinatura = models.TextField(blank=True)
    data_finalizado = models.DateTimeField(null=True)
    finalizado = models.BooleanField(default=False)

    assinantes = models.ManyToManyField('contrib.Defensoria',
                                        through='Assinatura',
                                        through_fields=('documento', 'defensoria')
                                        )

    versao_numero = models.PositiveIntegerField(default=1, auto_created=True, editable=False)
    tipo_documento = models.ForeignKey(TipoDocumento, null=True, on_delete=models.SET_NULL,
                                       verbose_name='Tipo do Documento')

    # cancelado_por = models.ForeignKey(to='auth.User', null=True,
    #                                    blank=True, on_delete=models.SET_NULL, editable=False)
    #
    # cancelado_em = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False)
    #
    # cancelado_por_nome = models.CharField(max_length=255, blank=True)
    #

    # auditoria
    cadastrado_por = models.ForeignKey(to='auth.User',
                                       related_name="%(app_label)s_%(class)s_cadastrado_por",
                                       editable=False)
    cadastrado_por_nome = models.CharField(max_length=255, blank=True)
    cadastrado_em = models.DateTimeField(auto_now_add=True, editable=False)

    modificado_por = models.ForeignKey(to='auth.User', null=True,
                                       blank=True, on_delete=models.SET_NULL, editable=False)
    modificado_em = models.DateTimeField(auto_now=True, blank=True, null=True, editable=False)

    modificado_por_nome = models.CharField(max_length=255, blank=True)

    versoes = HistoricalRecords()

    def pode_editar(self, usuario_atual):
        agora = datetime.now()
        usuario_atual_pode_editar = self.donos.filter(
            Q(all_atuacoes__ativo=True) &
            Q(all_atuacoes__data_inicial__lte=agora) &
            (
                Q(all_atuacoes__data_final__gte=agora) |
                Q(all_atuacoes__data_final=None)
            ) &
            (
                Q(all_atuacoes__defensor__servidor__usuario=usuario_atual) |
                Q(all_atuacoes__defensor__assessores__servidor__usuario=usuario_atual)
            )
        ).exists()

        return usuario_atual_pode_editar

    def pode_visualizar(self, usuario_atual):
        if self.pode_editar(usuario_atual):
            return True
        else:
            agora = datetime.now()
            usuario_atual_pode_visualizar = self.assinaturas.filter(
                Q(defensoria__all_atuacoes__ativo=True) &
                Q(defensoria__all_atuacoes__data_inicial__lte=agora) &
                (
                    Q(defensoria__all_atuacoes__data_final__gte=agora) |
                    Q(defensoria__all_atuacoes__data_final=None)
                ) &
                (
                    Q(defensoria__all_atuacoes__defensor__servidor__usuario=usuario_atual) |
                    Q(defensoria__all_atuacoes__defensor__assessores__servidor__usuario=usuario_atual)
                )
            ).exists()

            return usuario_atual_pode_visualizar

    def adicionar_assinantes(self, defensorias_assinantes, cadastrado_por):
        for defensoria in defensorias_assinantes:
            assinatura = self.assinantes.through(
                documento=self,
                defensoria=defensoria,
                cadastrado_por=cadastrado_por
            )
            assinatura.save()

    def revogar_assinaturas(self, usuario_atual):
        assinaturas = self.assinaturas.filter(ativo=True, esta_assinado=True)
        for assinatura in assinaturas:
            assinatura.revogar(usuario_atual=usuario_atual)
            self.adicionar_assinantes(
                defensorias_assinantes=(assinatura.defensoria,),
                cadastrado_por=usuario_atual
            )

    def assinar(self, defensoria, usuario_assinante):
        try:
            assinatura = self.assinaturas.get(
                defensoria=defensoria,
                ativo=True,
                esta_assinado=False
            )
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

        except self.assinantes.through.DoesNotExist as e:
            logger.error(e)
            raise e

    def finalizar_documento(self, usuario):
        if self.assinaturas.filter(ativo=True, esta_assinado=False).exists():
            raise ExitemAssinaturasPendentes()
        self.hash_assinatura = self.gerar_hash()
        self.data_finalizado = datetime.now()
        self.finalizado = True

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
        if self.assinado_por:
            print(self.assinado_por.pk, ':', self.assinado_por.get_full_name())
        super(Documento, self).save(*args, **kwargs)
