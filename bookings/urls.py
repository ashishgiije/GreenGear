from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:equipment_id>/', views.booking_create, name='create'),
    path('<int:booking_id>/', views.booking_detail, name='detail'),
    path('farmer/', views.farmer_bookings, name='farmer_list'),
    path('owner/', views.owner_bookings, name='owner_list'),
    path('update/<int:booking_id>/<str:status>/', views.update_booking_status, name='update_status'),
]