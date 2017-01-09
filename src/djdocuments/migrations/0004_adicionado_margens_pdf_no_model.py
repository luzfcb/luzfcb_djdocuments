# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djdocuments', '0003_unaccent_pg_extension'),
    ]

    operations = [
        migrations.AddField(
            model_name='documento',
            name='page_margin_bottom',
            field=models.FloatField(default=35.5, help_text='Margem inferior em rela\xe7\xe3o a pagina', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='page_margin_left',
            field=models.FloatField(default=1.0, help_text='Margem esquerda em rela\xe7\xe3o a pagina', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='page_margin_right',
            field=models.FloatField(default=4.0, help_text='Margem direita em rela\xe7\xe3o a pagina', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='documento',
            name='page_margin_top',
            field=models.FloatField(default=41.5, help_text='Margem superior em rela\xe7\xe3o a pagina', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='page_margin_bottom',
            field=models.FloatField(default=35.5, help_text='Margem inferior em rela\xe7\xe3o a pagina', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='page_margin_left',
            field=models.FloatField(default=1.0, help_text='Margem esquerda em rela\xe7\xe3o a pagina', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='page_margin_right',
            field=models.FloatField(default=4.0, help_text='Margem direita em rela\xe7\xe3o a pagina', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='historicaldocumento',
            name='page_margin_top',
            field=models.FloatField(default=41.5, help_text='Margem superior em rela\xe7\xe3o a pagina', null=True, blank=True),
        ),
    ]
