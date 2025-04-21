from django.urls import path
from . import views

app_name = 'pocos_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('gerar-tabela/', views.gerar_tabela, name='gerar_tabela'),
    path('exportar-xlsx/', views.exportar_xlsx, name='exportar_xlsx'),
]
