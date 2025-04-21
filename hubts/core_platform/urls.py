from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('core/', include('core.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('caronas/', include('caronas_app.urls')),
    path('pocos/', include('pocos_app.urls')),
    path('', include('core.landing_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
