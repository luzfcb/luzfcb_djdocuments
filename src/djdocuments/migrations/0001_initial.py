# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-05 19:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assinatura',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('versao_documento', models.PositiveIntegerField(null=True)),
                ('nome_defensoria', models.CharField(blank=True, max_length=255)),
                ('assinado_nome', models.CharField(blank=True, max_length=255)),
                ('assinado_em', models.DateTimeField(blank=True, null=True)),
                ('hash_assinatura', models.TextField(blank=True)),
                ('esta_assinado', models.BooleanField(default=False)),
                ('ativo', models.BooleanField(default=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True)),
                ('nome_cadastrado_por', models.CharField(blank=True, max_length=255)),
                ('nome_excluido_por', models.CharField(blank=True, max_length=255)),
                ('data_exclusao', models.DateTimeField(null=True)),
                ('assinado_por', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djdocuments_assinatura_assinaturas', to=settings.AUTH_USER_MODEL)),
                ('cadastrado_por', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='djdocuments_assinatura_cadastrado_por', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('versao_numero', models.PositiveIntegerField(auto_created=True, default=1, editable=False)),
                ('uuid_hash', models.UUIDField(db_index=True, editable=False, null=True, unique=True)),
                ('assunto', models.CharField(blank=True, max_length=255)),
                ('cabecalho', models.TextField(blank=True)),
                ('titulo', models.TextField(blank=True)),
                ('conteudo', models.TextField(blank=True)),
                ('rodape', models.TextField(blank=True)),
                ('eh_template', models.BooleanField(default=False)),
                ('template_descricao', models.TextField(blank=True)),
                ('assinatura_hash', models.TextField(blank=True, editable=False, null=True, unique=True)),
                ('esta_assinado', models.BooleanField(default=False)),
                ('data_finalizado', models.DateTimeField(null=True)),
                ('finalizado', models.BooleanField(default=False)),
                ('criado_por_nome', models.CharField(blank=True, max_length=255)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('modificado_em', models.DateTimeField(auto_now=True, null=True)),
                ('modificado_por_nome', models.CharField(blank=True, max_length=255)),
                ('esta_ativo', models.NullBooleanField(default=True, editable=False)),
                ('criado_por', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='djdocuments_documento_criado_por', to=settings.AUTH_USER_MODEL)),
                ('grupos_assinates', models.ManyToManyField(through='djdocuments.Assinatura', to='auth.Group')),
                ('modificado_por', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalDocumento',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('versao_numero', models.PositiveIntegerField(auto_created=True, default=1, editable=False)),
                ('uuid_hash', models.UUIDField(db_index=True, editable=False, null=True)),
                ('assunto', models.CharField(blank=True, max_length=255)),
                ('cabecalho', models.TextField(blank=True)),
                ('titulo', models.TextField(blank=True)),
                ('conteudo', models.TextField(blank=True)),
                ('rodape', models.TextField(blank=True)),
                ('eh_template', models.BooleanField(default=False)),
                ('template_descricao', models.TextField(blank=True)),
                ('assinatura_hash', models.TextField(blank=True, db_index=True, editable=False, null=True)),
                ('esta_assinado', models.BooleanField(default=False)),
                ('data_finalizado', models.DateTimeField(null=True)),
                ('finalizado', models.BooleanField(default=False)),
                ('criado_por_nome', models.CharField(blank=True, max_length=255)),
                ('criado_em', models.DateTimeField(blank=True, editable=False)),
                ('modificado_em', models.DateTimeField(blank=True, editable=False, null=True)),
                ('modificado_por_nome', models.CharField(blank=True, max_length=255)),
                ('esta_ativo', models.NullBooleanField(default=True, editable=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('criado_por', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('modificado_por', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(blank=True, max_length=255)),
                ('descricao', models.TextField(blank=True, max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='tipo_documento',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='djdocuments.TipoDocumento'),
        ),
        migrations.AddField(
            model_name='documento',
            name='tipo_documento',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='djdocuments.TipoDocumento', verbose_name='Tipo do Documento'),
        ),
        migrations.AddField(
            model_name='assinatura',
            name='documento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assinaturas', to='djdocuments.Documento'),
        ),
        migrations.AddField(
            model_name='assinatura',
            name='excluido_por',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='djdocuments_assinatura_excluido_por', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assinatura',
            name='grupo_assinante',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='djdocuments_assinatura_assinaturas', to='auth.Group'),
        ),
    ]
