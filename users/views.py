from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User
from equipment.models import Equipment
from bookings.models import Booking

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django.http import HttpResponse
from django.core.management import call_command

def run_migrations(request):
    call_command('makemigrations')
    call_command('migrate')
    return HttpResponse("Migrations completed!")


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        login_type = request.POST.get('login_type')
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password) and user.role == login_type:
                login(request, user)
                if user.role == 'farmer':
                    return redirect('users:farmer_dashboard')
                else:
                    return redirect('users:owner_dashboard')
            else:
                messages.error(request, 'Invalid credentials or role selection.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid credentials.')
    
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

def register_farmer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        location = request.POST.get('location')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'users/register_farmer.html')
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
                phone=phone,
                location=location,
                role='farmer'
            )
            messages.success(request, 'Registration successful! Please login.')
            return redirect('users:login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'users/register_farmer.html')

def register_owner(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        workshop_name = request.POST.get('workshop_name')
        address = request.POST.get('address')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'users/register_owner.html')
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
                phone=phone,
                workshop_name=workshop_name,
                address=address,
                role='owner'
            )
            messages.success(request, 'Registration successful! Please login.')
            return redirect('users:login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'users/register_owner.html')

@login_required
def profile(request):
    # Calculate statistics
    total_earnings = 0
    booking_requests_count = 0
    active_bookings_count = 0
    
    if request.user.role == 'owner':
        # Calculate total earnings from completed bookings
        completed_bookings = Booking.objects.filter(
            equipment__owner=request.user,
            status='completed'
        )
        total_earnings = sum(booking.total_amount for booking in completed_bookings)
        
        # Count pending booking requests
        booking_requests_count = Booking.objects.filter(
            equipment__owner=request.user,
            status='pending'
        ).count()
    elif request.user.role == 'farmer':
        # Count active bookings for farmers
        active_bookings_count = Booking.objects.filter(
            farmer=request.user,
            status__in=['pending', 'approved']
        ).count()
    
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.phone = request.POST.get('phone', '')
        user.location = request.POST.get('location', '')
        
        if user.role == 'owner':
            user.workshop_name = request.POST.get('workshop_name', '')
            user.address = request.POST.get('address', '')
        
        try:
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    context = {
        'total_earnings': total_earnings,
        'booking_requests_count': booking_requests_count,
        'active_bookings_count': active_bookings_count
    }
    return render(request, 'users/profile.html', context)

@login_required
def farmer_dashboard(request):
    if request.user.role != 'farmer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get farmer's bookings with counts
    bookings = Booking.objects.filter(farmer=request.user).select_related('equipment', 'equipment__owner')
    
    # Count bookings by status
    pending_count = bookings.filter(status='pending').count()
    approved_count = bookings.filter(status='approved').count()
    completed_count = bookings.filter(status='completed').count()
    
    # Get recent equipment for recommendations
    recommended_equipment = Equipment.objects.filter(availability=True).exclude(
        bookings__farmer=request.user
    ).select_related('owner').order_by('-created_at')[:3]
    
    context = {
        'bookings': bookings[:5],  # Show only recent 5 bookings
        'pending_count': pending_count,
        'approved_count': approved_count,
        'completed_count': completed_count,
        'recommended_equipment': recommended_equipment
    }
    return render(request, 'users/farmer_dashboard.html', context)

@login_required
def owner_dashboard(request):
    if request.user.role != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get owner's equipment
    equipment_list = Equipment.objects.filter(owner=request.user)
    
    # Get booking statistics
    pending_bookings = Booking.objects.filter(
        equipment__owner=request.user,
        status='pending'
    ).count()
    
    total_equipment = equipment_list.count()
    
    completed_bookings = Booking.objects.filter(
        equipment__owner=request.user,
        status='completed'
    )
    total_earnings = sum(booking.total_amount for booking in completed_bookings)
    
    recent_booking_requests = Booking.objects.filter(
        equipment__owner=request.user
    ).select_related('farmer', 'equipment').order_by('-created_at')[:3]
    
    context = {
        'equipment_list': equipment_list[:4],  # Show only first 4 equipment
        'pending_bookings_count': pending_bookings,
        'total_equipment': total_equipment,
        'total_earnings': total_earnings,
        'completed_bookings_count': completed_bookings.count(),
        'booking_requests': recent_booking_requests
    }

    return render(request, 'users/owner_dashboard.html', context)
