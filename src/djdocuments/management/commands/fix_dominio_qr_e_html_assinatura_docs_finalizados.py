# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import sys
import logging

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand, CommandError

from datetime import datetime, time
from dateutil.parser import parse
from django.template.loader import render_to_string
from django.db.models import Q

try:
    from django.urls import reverse
except ImportError:
    # django <= 1.9
    from django.core.urlresolvers import reverse

from django.test import RequestFactory

from bulk_update.helper import bulk_update

from djdocuments.utils.base64utils import gerar_tag_img_base64_png_qr_str
from django.utils.six.moves.urllib.parse import urlparse
from django.utils import six
from django.db.models import Prefetch
from djdocuments.backends import get_djdocuments_backend
from djdocuments.models import Documento, Assinatura

logger = logging.getLogger(__name__)


# url_dominio_antigo = "http://solar.defensoria.to.gov.br"
# data_limite_str = "2018-02-28"


def get_queryset_e_qnt_documentos_a_serem_afetados(data_final, data_inicial=None):
    backend = get_djdocuments_backend()

    max_data_limite = datetime.combine(data_final, time.max)

    q = Q(esta_assinado=True)
    q &= Q(rodape_qr_validacao='')
    q &= Q(conteudo_assinaturas='')
    q &= Q(data_assinado__lte=max_data_limite)
    if data_inicial:

        min_data_inicial = datetime.combine(data_inicial, time.min)
        q &= Q(data_assinado__gte=min_data_inicial)
        if max_data_limite < min_data_inicial:
            pass
    documentos_queryset = Documento.objects.filter(q)
    qnt_documentos_afetados = documentos_queryset.only('id').count()

    documentos_queryset = documentos_queryset.only(
        'id',
        'pk_uuid',
        'versao_numero',
        'rodape_qr_validacao',
        'conteudo_assinaturas',
        'esta_assinado',
        'esta_ativo',
        'eh_modelo',
        'modificado_por',
        'grupo_dono__{}'.format(backend.group_name_atrib),
    ).select_related(
        'grupo_dono',
    ).prefetch_related(
        Prefetch(
            lookup='grupos_assinates',
            queryset=Assinatura.objects.only(
                'esta_assinado',
                'assinado_em',
                'assinado_nome'
            )
        )
    )
    return documentos_queryset, qnt_documentos_afetados


def popular_campo_rodape_qr_validacao_e_assinaturas(url_dominio_antigo, documentos_queryset):
    domain = urlparse(url_dominio_antigo).hostname
    request_factory = RequestFactory(SERVER_NAME=domain)

    quantidade_registros_afetados = documentos_queryset.count()
    logger.info("Numero de registro a serem afetados: {}".format(quantidade_registros_afetados))
    logger.info("Iniciando Processamento, aguarde, isso pode demorar varios minutos")
    for document_object in documentos_queryset:
        finalizar_url = reverse(
            viewname='documentos:finalizar_assinatura',
            kwargs={
                'slug': document_object.pk_uuid
            }
        )
        request = request_factory.get(finalizar_url)
        request.user = document_object.modificado_por
        img_tag = gerar_tag_img_base64_png_qr_str(request, document_object)
        context = {
            'request': request,
            'object': document_object,
            'qr_code_validation_html_img_tag': img_tag
        }
        rodape_qr_validacao = render_to_string(
            template_name='luzfcb_djdocuments/documento_finalizado_rodape_qr_validacao.html',
            context=context
        )
        document_object.rodape_qr_validacao = rodape_qr_validacao
        _ = document_object.popular_conteudo_assinaturas()

    logger.info("Iniciando atualização em banco, aguarde, isso pode demorar varios minutos")
    bulk_update(documentos_queryset, update_fields=['rodape_qr_validacao', 'conteudo_assinaturas'], batch_size=100)


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument(
            '-d', '--dominio-url',
            action='store',
            dest='dominio',
            required=True,
            help='Especifique a URL dominio que constara na assinaturas e codigo QR de finalizacao do documentos'
        )
        parser.add_argument(
            '-f', '--dtfinal',
            action='store',
            dest='dtfinal',
            required=True,
            type=parse,
            help='Data final no formato AAAA-MM-DD'
        )
        parser.add_argument(
            '-i', '--dtinicio',
            action='store',
            dest='dtinicio',
            default=None,
            required=False,
            type=parse,
            help='Data inicial no formato AAAA-MM-DD'
        )
        parser.add_argument(
            '-p', '--pks',
            action='store_true',
            dest='mostrar_pks',
            default=False,
            required=False,
            help="Retorna as pks do Documentos GED envolvidos, mas nao executa"
        )

    def handle(self, *args, **options):
        msg_cancelar = "Execucao cancelada pelo usuario"
        messages = [u'\n']

        dominio = options.get('dominio', None)
        dtinicio = options.get('dtinicio', None)
        dtfinal = options.get('dtfinal', None)
        mostrar_pks = options.get('mostrar_pks', False)

        if not dtinicio:
            dtinicio = datetime(1970, 1, 1)
        if dtinicio:
            dtinicio = datetime.combine(dtinicio, time.min)
        if dtfinal:
            dtfinal = datetime.combine(dtfinal, time.max)

        if dtinicio and dtinicio > dtfinal:
            msg = "dtinicio ({dtinicio}) deve ser menor ou igual a dtfinal ({dtfinal})".format(
                dtinicio=dtinicio,
                dtfinal=dtfinal
            )
            print("\n")
            print(msg)
            sys.exit(0)
            # raise CommandError(msg)

        documentos_queryset, qnt_documentos_afetados = get_queryset_e_qnt_documentos_a_serem_afetados(
            data_final=dtfinal,
            data_inicial=dtinicio
        )
        msg_afetados = (
            u"Serao afetados {qnt_documentos_afetados} documentos do GED, "
            u"finalizados entre {dtinicio} e {dtfinal}.\n"
        ).format(
            qnt_documentos_afetados=qnt_documentos_afetados,
            dtinicio=dtinicio,
            dtfinal=dtfinal
        )
        if mostrar_pks:
            ids_documentos_afetados = ", ".join(
                (str(i) for i in sorted(tuple(documentos_queryset.values_list('id', flat=True))))
            )
            print(msg_afetados)
            print("\npks registros:\n")
            print(ids_documentos_afetados)
            print("\n")
            sys.exit(0)
            # raise CommandError(msg_cancelar)

        messages.append(
            u'Sera gerado os dados dos campos "rodape_qr_validacao" e "conteudo_assinaturas" do respectivo documento.\n'
            u'O dominio "{dominio}" sera utilizado como parte da url de validacao e codigo QR.\n'.format(
                dominio=dominio)
        )
        messages.append(
            msg_afetados
        )
        len(documentos_queryset)
        messages.append(
            u'Essa modificacao eh IRREVERSIVEL, voce tem certeza que deseja executar? [NAO/sim]: '
        )
        try:
            message = u''.join(messages)
            entrada = raw_input(message)
            if not six.text_type(entrada).strip().lower() in [u'yes', u'y', u's', u'sim']:
                raise CommandError(msg_cancelar)
        except KeyboardInterrupt:
            print(msg_cancelar)
            sys.exit(0)
            # raise CommandError(msg_cancelar)
        except SyntaxError:
            print(msg_cancelar)
            sys.exit(0)
            # raise CommandError(msg_cancelar)

        print("Iniciando execução. Isto pode demorar varios minutos")
        tempo_inicial = datetime.now()
        popular_campo_rodape_qr_validacao_e_assinaturas(dominio, documentos_queryset)
        tempo_final = datetime.now()
        tempo_total = relativedelta(tempo_final, tempo_inicial)
        print("Executado em {h}h {m}m {s}s".format(h=tempo_total.hours, m=tempo_total.minutes, s=tempo_total.seconds))
        sys.exit(0)
