from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    path('', views.equipment_list, name='list'),
    path('<int:equipment_id>/', views.equipment_detail, name='detail'),
    path('add/', views.equipment_add, name='add'),
    path('<int:equipment_id>/edit/', views.equipment_edit, name='edit'),
    path('<int:equipment_id>/delete/', views.equipment_delete, name='delete'),
]