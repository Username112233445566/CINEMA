from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cinema/', include('cinema_app.urls')),
    path('', RedirectView.as_view(url='/cinema/')),
    path('accounts/', include('django.contrib.auth.urls')),
]
from django.conf import settings
from django.conf.urls.static import static


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)