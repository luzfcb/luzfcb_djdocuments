# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assinatura',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('versao_documento', models.PositiveIntegerField(null=True)),
                ('nome_defensoria', models.CharField(max_length=255, blank=True)),
                ('assinado_nome', models.CharField(max_length=255, blank=True)),
                ('assinado_em', models.DateTimeField(null=True, blank=True)),
                ('hash_assinatura', models.TextField(blank=True)),
                ('esta_assinado', models.BooleanField(default=False, editable=False)),
                ('esta_ativo', models.NullBooleanField(default=True, editable=False)),
                ('ativo', models.BooleanField(default=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True)),
                ('nome_cadastrado_por', models.CharField(max_length=255, blank=True)),
                ('nome_excluido_por', models.CharField(max_length=255, blank=True)),
                ('data_exclusao', models.DateTimeField(null=True)),
                ('assinado_por', models.ForeignKey(related_name='djdocuments_assinatura_assinaturas', to=settings.AUTH_USER_MODEL, null=True)),
                ('cadastrado_por', models.ForeignKey(related_name='djdocuments_assinatura_cadastrado_por', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('versao_numero', models.PositiveIntegerField(default=1, editable=False, auto_created=True)),
                ('pk_uuid', models.UUIDField(null=True, default=uuid.uuid4, editable=False, unique=True, db_index=True)),
                ('assunto', models.CharField(max_length=255, blank=True)),
                ('cabecalho', models.TextField(blank=True)),
                ('titulo', models.TextField(blank=True)),
                ('conteudo', models.TextField(blank=True)),
                ('rodape', models.TextField(blank=True)),
                ('eh_template', models.BooleanField(default=False)),
                ('template_descricao', models.TextField(blank=True)),
                ('assinatura_hash', models.TextField(unique=True, null=True, editable=False, blank=True)),
                ('data_assinado', models.DateTimeField(null=True)),
                ('esta_assinado', models.BooleanField(default=False)),
                ('esta_pronto_para_assinar', models.BooleanField(default=False)),
                ('criado_por_nome', models.CharField(max_length=255, blank=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('modificado_por_nome', models.CharField(max_length=255, blank=True)),
                ('esta_ativo', models.NullBooleanField(default=True, editable=False)),
                ('criado_por', models.ForeignKey(related_name='djdocuments_documento_criado_por', on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('grupos_assinates', models.ManyToManyField(to='auth.Group', through='djdocuments.Assinatura')),
                ('modificado_por', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalDocumento',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('versao_numero', models.PositiveIntegerField(default=1, editable=False, auto_created=True)),
                ('pk_uuid', models.UUIDField(default=uuid.uuid4, null=True, editable=False, db_index=True)),
                ('assunto', models.CharField(max_length=255, blank=True)),
                ('cabecalho', models.TextField(blank=True)),
                ('titulo', models.TextField(blank=True)),
                ('conteudo', models.TextField(blank=True)),
                ('rodape', models.TextField(blank=True)),
                ('eh_template', models.BooleanField(default=False)),
                ('template_descricao', models.TextField(blank=True)),
                ('assinatura_hash', models.TextField(db_index=True, null=True, editable=False, blank=True)),
                ('data_assinado', models.DateTimeField(null=True)),
                ('esta_assinado', models.BooleanField(default=False)),
                ('esta_pronto_para_assinar', models.BooleanField(default=False)),
                ('criado_por_nome', models.CharField(max_length=255, blank=True)),
                ('criado_em', models.DateTimeField(editable=False, blank=True)),
                ('modificado_em', models.DateTimeField(null=True, editable=False, blank=True)),
                ('modificado_por_nome', models.CharField(max_length=255, blank=True)),
                ('esta_ativo', models.NullBooleanField(default=True, editable=False)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('criado_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical documento',
            },
        ),
        migrations.CreateModel(
            name='TipoDocumento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('titulo', models.CharField(max_length=255, blank=True)),
                ('descricao', models.TextField(max_length=255, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='tipo_documento',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING, db_constraint=False, blank=True, to='djdocuments.TipoDocumento', null=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='tipo_documento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Tipo do Documento', to='djdocuments.TipoDocumento', null=True),
        ),
        migrations.AddField(
            model_name='assinatura',
            name='documento',
            field=models.ForeignKey(related_name='assinaturas', to='djdocuments.Documento'),
        ),
        migrations.AddField(
            model_name='assinatura',
            name='excluido_por',
            field=models.ForeignKey(related_name='djdocuments_assinatura_excluido_por', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='assinatura',
            name='grupo_assinante',
            field=models.ForeignKey(related_name='djdocuments_assinatura_assinaturas', to='auth.Group'),
        ),
    ]