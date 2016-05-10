# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import django.db.models.deletion
from django.conf import settings


def populate_initial_data(apps, schema_editor):
    TipoDocumento = apps.get_model("luzfcb_djdocuments", "TipoDocumento")
    Documento = apps.get_model("luzfcb_djdocuments", "Documento")

    initial_data = [
        {'titulo': "OFICIO", 'descricao': "OFICIO"},
        {'titulo': "MEMORANDO", 'descricao': "MEMORANDO"},
    ]
    for data in initial_data:
        tipod = TipoDocumento(titulo=data['titulo'], descricao=data['descricao'])
        tipod.save()

    for tipo in TipoDocumento.objects.all():
        doc = Documento(
            cabecalho='teste',
            titulo='teste',
            conteudo='teste',
            rodape='teste',
            eh_template=True,
            template_descricao='teste',
            tipo_documento=tipo
        )
        doc.save()


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assinatura',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('versao_numero', models.IntegerField(null=True, editable=False)),
                ('assinatura_hash', models.TextField(unique=True, null=True, editable=False, blank=True)),
                ('esta_assinado', models.BooleanField(default=False)),
                ('assinado_em', models.DateTimeField(null=True, editable=False, blank=True)),
                ('assinado_por', models.ForeignKey(related_name='luzfcb_djdocuments_assinatura_assinado_por',
                                                   on_delete=django.db.models.deletion.SET_NULL, blank=True,
                                                   editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('revertido_da_versao',
                 models.IntegerField(default=None, editable=False, null=True, auto_created=True, blank=True)),
                ('versao_numero', models.IntegerField(default=1, editable=False, auto_created=True)),
                ('assunto', models.CharField(max_length=255, blank=True)),
                ('cabecalho', models.TextField(blank=True)),
                ('titulo', models.TextField(blank=True)),
                ('conteudo', models.TextField(blank=True)),
                ('rodape', models.TextField(blank=True)),
                ('eh_template', models.BooleanField(default=False)),
                ('template_descricao', models.TextField(blank=True)),
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
                ('assinado_por', models.ForeignKey(related_name='luzfcb_djdocuments_documento_assinado_por',
                                                   on_delete=django.db.models.deletion.SET_NULL, blank=True,
                                                   editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('assinantes',
                 models.ManyToManyField(related_name='luzfcb_djdocuments_documento_assinantes', editable=False,
                                        to=settings.AUTH_USER_MODEL, through='luzfcb_djdocuments.Assinatura',
                                        blank=True)),
                ('assinatura_removida_por',
                 models.ForeignKey(related_name='luzfcb_djdocuments_documento_assinatura_removida_por',
                                   on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False,
                                   to=settings.AUTH_USER_MODEL, null=True)),
                ('bloqueado_por', models.ForeignKey(related_name='luzfcb_djdocuments_documento_bloqueado_por',
                                                    on_delete=django.db.models.deletion.SET_NULL, blank=True,
                                                    editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('criado_por', models.ForeignKey(related_name='luzfcb_djdocuments_documento_criado_por',
                                                 on_delete=django.db.models.deletion.SET_NULL, blank=True,
                                                 editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', models.ForeignKey(related_name='luzfcb_djdocuments_documento_modificado_por',
                                                     on_delete=django.db.models.deletion.SET_NULL, blank=True,
                                                     editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('revertido_por', models.ForeignKey(related_name='luzfcb_djdocuments_documento_revertido_por',
                                                    on_delete=django.db.models.deletion.SET_NULL, blank=True,
                                                    editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['criado_em'],
                'verbose_name': 'Documento Digital',
                'verbose_name_plural': 'Documentos Digitais',
                'permissions': (
                    ('pode_criar_documento', 'Pode Criar documento'),
                    ('pode_editar_documento', 'Pode Editar documento'),
                    ('pode_assinar_documento', 'Pode Assinar documento'),
                    ('pode_desativar_documento', 'Pode Desativar documento'),
                    ('pode_visualizar_versoes_anteriores_documento', 'Pode Visualizar versoes anteriores de documento'),
                    (
                        'pode_reverter_para_uma_versao_anterior_documento',
                        'Pode Reverter documento para uma vers\xe3o anterior'),
                    ('pode_imprimir', 'Pode Imprimir documento')),
            },
        ),
        migrations.CreateModel(
            name='HistoricalDocumento',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', db_index=True, auto_created=True, blank=True)),
                ('revertido_da_versao',
                 models.IntegerField(default=None, editable=False, null=True, auto_created=True, blank=True)),
                ('versao_numero', models.IntegerField(default=1, editable=False, auto_created=True)),
                ('assunto', models.CharField(max_length=255, blank=True)),
                ('cabecalho', models.TextField(blank=True)),
                ('titulo', models.TextField(blank=True)),
                ('conteudo', models.TextField(blank=True)),
                ('rodape', models.TextField(blank=True)),
                ('eh_template', models.BooleanField(default=False)),
                ('template_descricao', models.TextField(blank=True)),
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
                ('history_type',
                 models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('assinado_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING,
                                                   db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL,
                                                   null=True)),
                ('assinatura_removida_por',
                 models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING,
                                   db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('bloqueado_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING,
                                                    db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL,
                                                    null=True)),
                ('criado_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING,
                                                 db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL,
                                                 null=True)),
                ('history_user', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.SET_NULL,
                                                   to=settings.AUTH_USER_MODEL, null=True)),
                ('modificado_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING,
                                                     db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL,
                                                     null=True)),
                ('revertido_por', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING,
                                                    db_constraint=False, blank=True, to=settings.AUTH_USER_MODEL,
                                                    null=True)),
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
                ('titulo', models.CharField(max_length=255, blank=True)),
                ('descricao', models.TextField(max_length=255, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='tipo_documento',
            field=models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING,
                                    db_constraint=False, blank=True, to='luzfcb_djdocuments.TipoDocumento', null=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='tipo_documento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Tipo do Documento',
                                    to='luzfcb_djdocuments.TipoDocumento', null=True),
        ),
        migrations.AddField(
            model_name='assinatura',
            name='documento',
            field=models.ForeignKey(related_name='luzfcb_djdocuments_assinatura_documento',
                                    on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False,
                                    to='luzfcb_djdocuments.Documento', null=True),
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
        migrations.AlterUniqueTogether(
            name='assinatura',
            unique_together=set([('documento', 'assinado_por', 'versao_numero')]),
        ),
        #
        migrations.RunPython(populate_initial_data),

    ]
