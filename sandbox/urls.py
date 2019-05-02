try:
    from django.conf.urls.defaults import *
except ImportError as e:
    from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import django.conf.urls.i18n
from django.conf.urls.static import static

from apps.app import shop

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^i18n/', include(django.conf.urls.i18n)),
    url(r'', include(shop.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
            ]
