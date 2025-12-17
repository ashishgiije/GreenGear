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

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum

def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    from equipment.models import Equipment
    from bookings.models import Booking
    
    # Statistics
    total_users = User.objects.count()
    farmer_count = User.objects.filter(role='farmer').count()
    owner_count = User.objects.filter(role='owner').count()
    
    total_equipment = Equipment.objects.count()
    available_equipment = Equipment.objects.filter(availability=True).count()
    
    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(status__in=['pending', 'approved']).count()
    completed_bookings = Booking.objects.filter(status='completed').count()
    
    total_revenue = Booking.objects.filter(status='completed').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Recent data
    recent_users = User.objects.all().order_by('-date_joined')[:5]
    recent_equipment = Equipment.objects.all().order_by('-created_at')[:5]
    recent_bookings = Booking.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'farmer_count': farmer_count,
        'owner_count': owner_count,
        'total_equipment': total_equipment,
        'available_equipment': available_equipment,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'completed_bookings': completed_bookings,
        'total_revenue': total_revenue,
        'recent_users': recent_users,
        'recent_equipment': recent_equipment,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'users/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.all().order_by('-date_joined')
    
    # Handle search
    search_query = request.GET.get('q', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Handle role filter
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    context = {
        'users': users,
        'search_query': search_query,
        'role_filter': role_filter
    }
    return render(request, 'users/manage_users.html', context)

@login_required
@user_passes_test(is_admin)
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        location = request.POST.get('location')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                location=location
            )
            messages.success(request, f'User "{username}" created successfully!')
            return redirect('users:manage_users')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
    
    return render(request, 'users/create_user.html')

@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone = request.POST.get('phone')
        user.location = request.POST.get('location')
        user.workshop_name = request.POST.get('workshop_name', '')
        user.address = request.POST.get('address', '')
        
        if request.POST.get('password'):
            user.set_password(request.POST.get('password'))
        
        try:
            user.save()
            messages.success(request, f'User "{user.username}" updated successfully!')
            return redirect('users:manage_users')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
    
    context = {'user': user}
    return render(request, 'users/edit_user.html', context)

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted successfully!')
        return redirect('users:manage_users')
    
    context = {'user': user}
    return render(request, 'users/delete_user.html', context)


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
        total_earnings = completed_bookings.aggregate(
            total_sum=Sum('total_amount')
        )['total_sum'] or 0
        
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
    
    # Get pending booking requests count
    pending_bookings = Booking.objects.filter(
        equipment__owner=request.user,
        status='pending'
    ).count()
    
    # Get total equipment count
    total_equipment = equipment_list.count()
    
    # Calculate total earnings from COMPLETED bookings
    completed_bookings = Booking.objects.filter(
        equipment__owner=request.user,
        status='completed'
    )
    
    # Sum total_amount from all completed bookings
    total_earnings = completed_bookings.aggregate(
        total_sum=Sum('total_amount')
    )['total_sum'] or 0
    
    # Get completed bookings count
    completed_bookings_count = completed_bookings.count()
    
    # Get recent booking requests for display
    recent_booking_requests = Booking.objects.filter(
        equipment__owner=request.user
    ).select_related('farmer', 'equipment').order_by('-created_at')[:3]
    
    context = {
        'equipment_list': equipment_list[:4],  # Show only first 4 equipment
        'pending_bookings_count': pending_bookings,
        'total_equipment': total_equipment,
        'total_earnings': total_earnings,
        'completed_bookings_count': completed_bookings_count,
        'booking_requests': recent_booking_requests
    }
    return render(request, 'users/owner_dashboard.html', context)