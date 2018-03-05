# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import base64
import io

import pyqrcode
from django.core.urlresolvers import reverse
from urlobject import URLObject

from ..templatetags.luzfcb_djdocuments_tags import absolute_uri


def png_as_base64_str(qr_code, scale=3, module_color=(0, 0, 0, 255),
                      background=(255, 255, 255, 255), quiet_zone=4):
    with io.BytesIO() as virtual_file:
        qr_code.png(file=virtual_file, scale=scale, module_color=module_color,
                    background=background, quiet_zone=quiet_zone)
        image_as_str = base64.b64encode(virtual_file.getvalue()).decode("ascii")
    return image_as_str


def gerar_tag_img_base64_png_qr_str(request, document_object):
    # http://stackoverflow.com/a/7389616/2975300

    # possivel candidato para cache
    url_validar = reverse('documentos:validar')
    querystring = "{}={}".format('h', document_object.get_assinatura_hash_upper_limpo)
    url_com_querystring = URLObject(url_validar).with_query(querystring)
    url = absolute_uri(url_com_querystring, request)

    codigo_qr = pyqrcode.create(url)
    encoded_image = png_as_base64_str(qr_code=codigo_qr, scale=2)

    img_tag = "<img src=data:image/png;base64,{}>".format(encoded_image)
    return img_tag
