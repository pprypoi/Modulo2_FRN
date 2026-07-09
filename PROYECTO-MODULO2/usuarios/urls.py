from django.urls import path
from . import views


urlpatterns = [
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
]