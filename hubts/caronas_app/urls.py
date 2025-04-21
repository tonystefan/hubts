from django.urls import path
from . import views

app_name = 'caronas_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('rotas/', views.route_list, name='route_list'),
    path('rotas/nova/', views.route_create, name='route_create'),
    path('rotas/<int:pk>/editar/', views.route_update, name='route_update'),
    path('rotas/<int:pk>/excluir/', views.route_delete, name='route_delete'),
    
    path('veiculos/', views.vehicle_list, name='vehicle_list'),
    path('veiculos/novo/', views.vehicle_create, name='vehicle_create'),
    path('veiculos/<int:pk>/editar/', views.vehicle_update, name='vehicle_update'),
    path('veiculos/<int:pk>/excluir/', views.vehicle_delete, name='vehicle_delete'),
    
    path('precos-combustivel/', views.fuel_price_list, name='fuel_price_list'),
    path('precos-combustivel/novo/', views.fuel_price_create, name='fuel_price_create'),
    path('precos-combustivel/<int:pk>/editar/', views.fuel_price_update, name='fuel_price_update'),
    path('precos-combustivel/<int:pk>/excluir/', views.fuel_price_delete, name='fuel_price_delete'),
    
    path('caronas/', views.carpool_list, name='carpool_list'),
    path('caronas/nova/', views.carpool_create, name='carpool_create'),
    path('caronas/<int:pk>/', views.carpool_detail, name='carpool_detail'),
    path('caronas/<int:pk>/editar/', views.carpool_update, name='carpool_update'),
    path('caronas/<int:pk>/excluir/', views.carpool_delete, name='carpool_delete'),
    path('caronas/<int:pk>/participantes/', views.carpool_participants, name='carpool_participants'),
    path('caronas/<int:carpool_pk>/participante/<int:pk>/pagar/', views.participant_mark_paid, name='participant_mark_paid'),
    
    path('relatorios/', views.reports, name='reports'),
    path('relatorios/usuario/<int:user_id>/', views.user_report, name='user_report'),
    path('relatorios/exportar/', views.export_report, name='export_report'),
    
    path('meu-saldo/', views.my_balance, name='my_balance'),
]
