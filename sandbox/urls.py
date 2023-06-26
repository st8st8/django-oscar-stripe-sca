from django.urls import include, path
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import static, i18n

from apps.app import shop

admin.autodiscover()

urlpatterns = [
    path('^admin/', include(admin.site.urls)),
    path('^i18n/', include(i18n)),
    path('', include(shop.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
            ]
