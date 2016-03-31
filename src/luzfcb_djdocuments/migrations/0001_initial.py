# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revertido_da_versao', models.IntegerField(default=None, editable=False, null=True, auto_created=True, blank=True)),
                ('versao_numero', models.IntegerField(default=1, editable=False, auto_created=True)),
                ('cabecalho', models.TextField(blank=True)),
                ('titulo', models.TextField(blank=True)),
                ('conteudo', models.TextField(blank=True)),
                ('rodape', models.TextField(blank=True)),
                ('eh_template', models.BooleanField(default=False)),
                ('criado_em', models.DateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('revertido_em', models.DateTimeField(null=True, editable=False, blank=True)),
                ('esta_ativo', models.NullBooleanField(default=True, editable=False)),
                ('esta_bloqueado', models.NullBooleanField(default=False, editable=False)),
                ('bloqueado_em', models.DateTimeField(null=True, editable=False, blank=True)),
                ('assinatura_hash', models.TextField(unique=True, null=True, editable=False, blank=True)),
                ('esta_assinado', models.BooleanField(default=False)),
                ('assinado_em', models.DateTimeField(null=True, editable=False, blank=True)),
                ('assinatura_removida_em', models.DateTimeField(null=True, editable=False, blank=True)),
                ('assinado_por', models.ForeignKey(related_name='luzfcb_djdocuments_documento_assinado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('assinatura_removida_por', models.ForeignKey(related_name='luzfcb_djdocuments_documento_assinatura_removida_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('bloqueado_por', models.ForeignKey(related_name='luzfcb_djdocuments_documento_bloqueado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('criado_por', models.ForeignKey(related_name='luzfcb_djdocuments_documento_criado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('modelo_documento', models.ForeignKey(related_name='documento_documentos', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='luzfcb_djdocuments.Documento', null=True)),
                ('modificado_por', models.ForeignKey(related_name='luzfcb_djdocuments_documento_modificado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('revertido_por', models.ForeignKey(related_name='luzfcb_djdocuments_documento_revertido_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['criado_em'],
                'verbose_name': 'Documento Digital',
                'verbose_name_plural': 'Documentos Digitais',
                'permissions': (('pode_criar_documento', 'Pode Criar documento'), ('pode_editar_documento', 'Pode Editar documento'), ('pode_assinar_documento', 'Pode Assinar documento'), ('pode_desativar_documento', 'Pode Desativar documento'), ('pode_visualizar_versoes_anteriores_documento', 'Pode Visualizar versoes anteriores de documento'), ('pode_reverter_para_uma_versao_anterior_documento', 'Pode Reverter documento para uma vers\xe3o anterior'), ('pode_imprimir', 'Pode Imprimir documento')),
            },
        ),
        migrations.CreateModel(
            name='HistoricalDocumento',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('revertido_da_versao', models.IntegerField(default=None, editable=False, null=True, auto_created=True, blank=True)),
                ('versao_numero', models.IntegerField(default=1, editable=False, auto_created=True)),
                ('cabecalho', models.TextField(blank=True)),
                ('titulo', models.TextField(blank=True)),
                ('conteudo', models.TextField(blank=True)),
                ('rodape', models.TextField(blank=True)),
                ('eh_template', models.BooleanField(default=False)),
                ('criado_em', models.DateTimeField(default=django.utils.timezone.now, editable=False, blank=True)),
                ('modificado_em', models.DateTimeField(null=True, editable=False, blank=True)),
                ('revertido_em', models.DateTimeField(null=True, editable=False, blank=True)),
                ('esta_ativo', models.NullBooleanField(default=True, editable=False)),
                ('esta_bloqueado', models.NullBooleanField(default=False, editable=False)),
                ('bloqueado_em', models.DateTimeField(null=True, editable=False, blank=True)),
                ('assinatura_hash', models.TextField(db_index=True, null=True, editable=False, blank=True)),
                ('esta_assinado', models.BooleanField(default=False)),
                ('assinado_em', models.DateTimeField(null=True, editable=False, blank=True)),
                ('assinatura_removida_em', models.DateTimeField(null=True, editable=False, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('assinado_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('assinatura_removida_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('bloqueado_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('criado_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('modelo_documento', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='luzfcb_djdocuments.Documento', null=True)),
                ('modificado_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('revertido_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical Documento Digital',
            },
        ),
        migrations.CreateModel(
            name='TipoDocumento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descricao', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='DocumentoTemplate',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('luzfcb_djdocuments.documento',),
        ),
    ]
