from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_usuario, name='login'),
    path('register/', views.registro_usuario, name='register'),
    path('refresh/', views.refresh_token, name='refresh_token'),
    path('perfil/', views.obtener_perfil, name='obtener_perfil'),
]