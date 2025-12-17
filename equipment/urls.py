from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    path('', views.equipment_list, name='list'),
    path('<int:equipment_id>/', views.equipment_detail, name='detail'),
    path('add/', views.equipment_add, name='add'),
    path('<int:equipment_id>/edit/', views.equipment_edit, name='edit'),
    path('<int:equipment_id>/delete/', views.equipment_delete, name='delete'),
    # Admin URLs
    path('admin/manage/', views.manage_all_equipment, name='manage_all'),
    path('admin/<int:equipment_id>/edit/', views.admin_edit_equipment, name='admin_edit'),
    path('admin/<int:equipment_id>/delete/', views.admin_delete_equipment, name='admin_delete'),
]