from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('perfil/', include('perfil.urls')),
    path('extrato/', include('extrato.urls')),
    path('planejamento/', include('planejamento.urls')),
    path('contas/', include('contas.urls'))
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #URL para as Imagens, estão sendo buscadaas a partir do "MEDIA_ROOT"
#que os direciona para a pasta "media/", assim fazendo com que a URL pegue as imagens da pasta com sucesso  