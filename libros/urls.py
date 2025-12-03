from django.urls import path
from . import views

app_name = 'libros'

urlpatterns = [
    path('', views.lista_libros, name='lista_libros'),
    path('libro/<int:tipo>/', views.detalle_libro, name='detalle_libro'),
]

