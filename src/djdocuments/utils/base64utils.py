# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import base64
import io


def png_as_base64_str(qr_code, scale=3, module_color=(0, 0, 0, 255),
                      background=(255, 255, 255, 255), quiet_zone=4):
    with io.BytesIO() as virtual_file:
        qr_code.png(file=virtual_file, scale=scale, module_color=module_color,
                    background=background, quiet_zone=quiet_zone)
        image_as_str = base64.b64encode(virtual_file.getvalue()).decode("ascii")
    return image_as_str
