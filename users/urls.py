from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/farmer/', views.register_farmer, name='register_farmer'),
    path('register/owner/', views.register_owner, name='register_owner'),
    path('profile/', views.profile, name='profile'),
    path('farmer/dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('change-password/', views.change_password, name='change_password'),
    # Add change password URL if needed
]