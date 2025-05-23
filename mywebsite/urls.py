
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_vies
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    

    path('', include('users.urls')),
    path('', include('django.contrib.auth.urls')),
    path('recipes/', include('recipes.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
