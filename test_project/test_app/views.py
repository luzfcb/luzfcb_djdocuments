from django.shortcuts import render  # noqa

from djdocuments.views.documentos import VincularDocumentoBaseView

from .models import Processo


# Create your views here.
class DocumentoProcessoVinculateView(VincularDocumentoBaseView):
    model = Processo
    documents_field_name = 'documentos'

    def dispatch(self, request, *args, **kwargs):
        return super(DocumentoProcessoVinculateView, self).dispatch(request, *args, **kwargs)
