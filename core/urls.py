from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('eliminar-billetera/', views.eliminar_billetera, name='eliminar_billetera'),
    path('', views.index, name='index'),
]
