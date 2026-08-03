from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('alumnos/', include('alumnos.urls')),
    path('docentes/', include('docentes.urls')),
    path('libros/', include('libros.urls')),
    path('', include('core.urls')),
]