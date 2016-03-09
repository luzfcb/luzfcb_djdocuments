# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.db import migrations, models
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('versao_numero', models.IntegerField(default=1, auto_created=True, editable=False)),
                ('revertido_da_versao', models.IntegerField(default=None, blank=True, null=True, auto_created=True, editable=False)),
                ('titulo', models.CharField(max_length=500, blank=True)),
                ('conteudo', models.TextField()),
                ('criado_em', models.DateTimeField(default=django.utils.timezone.now, blank=True, editable=False)),
                ('modificado_em', models.DateTimeField(null=True, auto_now=True)),
                ('revertido_em', models.DateTimeField(blank=True, null=True, editable=False)),
                ('esta_ativo', models.NullBooleanField(default=True, editable=False)),
                ('esta_bloqueado', models.NullBooleanField(default=False, editable=False)),
                ('bloqueado_em', models.DateTimeField(blank=True, null=True, editable=False)),
                ('assinatura_hash', models.TextField(unique=True, blank=True, null=True, editable=False)),
                ('esta_assinado', models.BooleanField(default=False)),
                ('assinado_em', models.DateTimeField(blank=True, null=True, editable=False)),
                ('assinatura_removida_em', models.DateTimeField(blank=True, null=True, editable=False)),
                ('assinado_por', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, related_name='luzfcb_djdocuments_documento_assinado_por', null=True, editable=False)),
                ('assinatura_removida_por', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, related_name='luzfcb_djdocuments_documento_assinatura_removida_por', null=True, editable=False)),
                ('bloqueado_por', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, related_name='luzfcb_djdocuments_documento_bloqueado_por', null=True, editable=False)),
                ('criado_por', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, related_name='luzfcb_djdocuments_documento_criado_por', null=True, editable=False)),
                ('modificado_por', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, related_name='luzfcb_djdocuments_documento_modificado_por', null=True, editable=False)),
                ('revertido_por', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, related_name='luzfcb_djdocuments_documento_revertido_por', null=True, editable=False)),
            ],
            options={
                'ordering': ['criado_em'],
                'permissions': (('pode_criar_documento', 'Pode Criar documento'), ('pode_editar_documento', 'Pode Editar documento'), ('pode_assinar_documento', 'Pode Assinar documento'), ('pode_desativar_documento', 'Pode Desativar documento'), ('pode_visualizar_versoes_anteriores_documento', 'Pode Visualizar versoes anteriores de documento'), ('pode_reverter_para_uma_versao_anterior_documento', 'Pode Reverter documento para uma versão anterior'), ('pode_imprimir', 'Pode Imprimir documento')),
            },
        ),
        migrations.CreateModel(
            name='HistoricalDocumento',
            fields=[
                ('id', models.IntegerField(db_index=True, verbose_name='ID', blank=True, auto_created=True)),
                ('versao_numero', models.IntegerField(default=1, auto_created=True, editable=False)),
                ('revertido_da_versao', models.IntegerField(default=None, blank=True, null=True, auto_created=True, editable=False)),
                ('titulo', models.CharField(max_length=500, blank=True)),
                ('conteudo', models.TextField()),
                ('criado_em', models.DateTimeField(default=django.utils.timezone.now, blank=True, editable=False)),
                ('modificado_em', models.DateTimeField(blank=True, null=True, editable=False)),
                ('revertido_em', models.DateTimeField(blank=True, null=True, editable=False)),
                ('esta_ativo', models.NullBooleanField(default=True, editable=False)),
                ('esta_bloqueado', models.NullBooleanField(default=False, editable=False)),
                ('bloqueado_em', models.DateTimeField(blank=True, null=True, editable=False)),
                ('assinatura_hash', models.TextField(blank=True, db_index=True, null=True, editable=False)),
                ('esta_assinado', models.BooleanField(default=False)),
                ('assinado_em', models.DateTimeField(blank=True, null=True, editable=False)),
                ('assinatura_removida_em', models.DateTimeField(blank=True, null=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('assinado_por', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to=settings.AUTH_USER_MODEL, null=True, db_constraint=False, related_name='+')),
                ('assinatura_removida_por', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to=settings.AUTH_USER_MODEL, null=True, db_constraint=False, related_name='+')),
                ('bloqueado_por', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to=settings.AUTH_USER_MODEL, null=True, db_constraint=False, related_name='+')),
                ('criado_por', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to=settings.AUTH_USER_MODEL, null=True, db_constraint=False, related_name='+')),
                ('history_user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True, related_name='+')),
                ('modificado_por', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to=settings.AUTH_USER_MODEL, null=True, db_constraint=False, related_name='+')),
                ('revertido_por', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, blank=True, to=settings.AUTH_USER_MODEL, null=True, db_constraint=False, related_name='+')),
            ],
            options={
                'verbose_name': 'historical documento',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
    ]
