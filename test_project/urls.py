"""test_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.i18n import javascript_catalog

from luzfcb_djdocuments import luzfcb_djdocuments_urls

urlpatterns = [
    url(r'', include(luzfcb_djdocuments_urls,
                     namespace='documentos')),

    url(r'^captcha/',
        include('captcha.urls'),
        ),

    url(r'^admin/', admin.site.urls),
    url(r'', include('django.contrib.auth.urls')),

    url(r'^accounts/login/$', auth_views.login),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()


js_info_dict = {
    'packages': ('your.app.package',),
}

urlpatterns += [
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript-catalog'),
]