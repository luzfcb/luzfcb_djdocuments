from dal import autocomplete
from django.db.models.query_utils import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from luzfcb_djdocuments.templatetags.luzfcb_djdocuments_tags import remover_tags_html
from luzfcb_djdocuments.views.documentos import USER_MODEL
from luzfcb_djdocuments.models import DocumentoTemplate, Documento


class UserAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view to Django User Based
    """

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return USER_MODEL.objects.none()

        qs = USER_MODEL.objects.all().order_by('first_name', 'last_name')

        if self.q:
            qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))

            # qs = qs.annotate(full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField()))
            # qs = qs.filter(full_name__icontains=self.q)
        return qs

    def get_result_label(self, result):
        return result.get_full_name().title()


class DocumentoTemplateAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view to Django User Based
    """

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return DocumentoTemplate.objects.none()

        qs = DocumentoTemplate.objects.all()

        if self.q:
            qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))

            # qs = qs.annotate(full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField()))
            # qs = qs.filter(full_name__icontains=self.q)
        return qs

    def get_result_label(self, result):
        return result.get_full_name().title()


class DocumentoCriarAutocomplete(autocomplete.Select2QuerySetView):

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(DocumentoCriarAutocomplete, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Documento.admin_objects.none()

        print('forwarded: ', self.forwarded)
        modelo_documento = self.forwarded.get('modelo_documento', None)

        qs = Documento.admin_objects.all()

        if modelo_documento:
            qs = qs.filter(modelo_documento=modelo_documento)

        # if self.q:
        #     qs = qs.filter(Q(first_name__icontains=self.q) | Q(last_name__icontains=self.q))
        #
        #     # qs = qs.annotate(full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField()))
        #     # qs = qs.filter(full_name__icontains=self.q)
        return qs

    def get_result_label(self, result):
        a = remover_tags_html(result.titulo)
        return a
