from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Equipment
from bookings.models import Booking
from django.contrib.auth.decorators import login_required, user_passes_test  # Add this import

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_all_equipment(request):
    equipment_list = Equipment.objects.all().select_related('owner').order_by('-created_at')
    
    # Handle search
    search_query = request.GET.get('q', '')
    if search_query:
        equipment_list = equipment_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(owner__username__icontains=search_query)
        )
    
    # Handle filters
    category_filter = request.GET.get('category', '')
    if category_filter:
        equipment_list = equipment_list.filter(category=category_filter)
    
    availability_filter = request.GET.get('availability', '')
    if availability_filter:
        equipment_list = equipment_list.filter(availability=(availability_filter == 'true'))
    
    context = {
        'equipment_list': equipment_list,
        'search_query': search_query,
        'category_filter': category_filter,
        'availability_filter': availability_filter
    }
    return render(request, 'equipment/manage_all.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_edit_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    
    if request.method == 'POST':
        equipment.name = request.POST.get('name')
        equipment.category = request.POST.get('category')
        equipment.description = request.POST.get('description')
        equipment.rent_per_day = request.POST.get('rent_per_day') or None
        equipment.rent_per_hour = request.POST.get('rent_per_hour') or None
        equipment.location = request.POST.get('location')
        equipment.availability = request.POST.get('availability') == 'on'
        
        if request.FILES.get('image'):
            equipment.image = request.FILES['image']
        
        equipment.save()
        messages.success(request, f'Equipment "{equipment.name}" updated successfully!')
        return redirect('equipment:manage_all')
    
    context = {
        'equipment': equipment
    }
    return render(request, 'equipment/admin_edit.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_delete_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    
    if request.method == 'POST':
        equipment_name = equipment.name
        equipment.delete()
        messages.success(request, f'Equipment "{equipment_name}" deleted successfully!')
        return redirect('equipment:manage_all')
    
    context = {
        'equipment': equipment
    }
    return render(request, 'equipment/admin_delete.html', context)


@login_required
def equipment_add(request):
    if request.user.role != 'owner':
        messages.error(request, 'Only equipment owners can add equipment.')
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        category = request.POST.get('category')
        description = request.POST.get('description')
        rent_per_day = request.POST.get('rent_per_day')
        rent_per_hour = request.POST.get('rent_per_hour')
        location = request.POST.get('location')
        availability = request.POST.get('availability') == 'on'
        image = request.FILES.get('image')
        
        try:
            equipment = Equipment.objects.create(
                owner=request.user,
                name=name,
                category=category,
                description=description,
                rent_per_day=rent_per_day or None,
                rent_per_hour=rent_per_hour or None,
                location=location,
                availability=availability,
                image=image
            )
            messages.success(request, f'Equipment "{name}" added successfully!')
            return redirect('users:owner_dashboard')
        except Exception as e:
            messages.error(request, f'Error adding equipment: {str(e)}')
    
    return render(request, 'equipment/add.html')

@login_required
def equipment_edit(request, equipment_id):
    if request.user.role != 'owner':
        messages.error(request, 'Only equipment owners can edit equipment.')
        return redirect('home')
    
    equipment = get_object_or_404(Equipment, id=equipment_id, owner=request.user)
    
    if request.method == 'POST':
        equipment.name = request.POST.get('name')
        equipment.category = request.POST.get('category')
        equipment.description = request.POST.get('description')
        equipment.rent_per_day = request.POST.get('rent_per_day') or None
        equipment.rent_per_hour = request.POST.get('rent_per_hour') or None
        equipment.location = request.POST.get('location')
        equipment.availability = request.POST.get('availability') == 'on'
        
        if request.FILES.get('image'):
            equipment.image = request.FILES['image']
        
        equipment.save()
        messages.success(request, f'Equipment "{equipment.name}" updated successfully!')
        return redirect('users:owner_dashboard')
    
    context = {
        'equipment': equipment
    }
    return render(request, 'equipment/edit.html', context)

@login_required
def equipment_delete(request, equipment_id):
    if request.user.role != 'owner':
        messages.error(request, 'Only equipment owners can delete equipment.')
        return redirect('home')
    
    equipment = get_object_or_404(Equipment, id=equipment_id, owner=request.user)
    
    if request.method == 'POST':
        equipment_name = equipment.name
        equipment.delete()
        messages.success(request, f'Equipment "{equipment_name}" deleted successfully!')
        return redirect('users:owner_dashboard')
    
    context = {
        'equipment': equipment
    }
    return render(request, 'equipment/delete.html', context)

def equipment_list(request):
    # Base queryset - only available equipment
    equipment_list = Equipment.objects.filter(availability=True).select_related('owner')
    
    # Show only owner's equipment if requested
    if request.GET.get('my_equipment') and request.user.is_authenticated and request.user.role == 'owner':
        equipment_list = Equipment.objects.filter(owner=request.user)
    
    # Handle search
    search_query = request.GET.get('q', '')
    if search_query:
        equipment_list = equipment_list.filter(
            Q(name__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Handle category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        equipment_list = equipment_list.filter(category=category_filter)
    
    # Handle location filter
    location_filter = request.GET.get('location', '')
    if location_filter:
        equipment_list = equipment_list.filter(location__icontains=location_filter)
    
    # Handle price range filter
    price_filter = request.GET.get('price_range', '')
    if price_filter:
        if price_filter == '0-500':
            equipment_list = equipment_list.filter(rent_per_day__lte=500)
        elif price_filter == '500-1000':
            equipment_list = equipment_list.filter(rent_per_day__gte=500, rent_per_day__lte=1000)
        elif price_filter == '1000-2000':
            equipment_list = equipment_list.filter(rent_per_day__gte=1000, rent_per_day__lte=2000)
        elif price_filter == '2000+':
            equipment_list = equipment_list.filter(rent_per_day__gte=2000)
    
    context = {
        'equipment_list': equipment_list,
        'search_query': search_query,
        'category_filter': category_filter,
        'location_filter': location_filter,
        'price_filter': price_filter
    }
    return render(request, 'equipment/list.html', context)

def equipment_detail(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    
    # Check if equipment is currently booked
    active_booking = Booking.objects.filter(
        equipment=equipment,
        status__in=['pending', 'approved']
    ).first()
    
    # Get similar equipment (same category, different owner, available)
    similar_equipment = Equipment.objects.filter(
        category=equipment.category,
        availability=True
    ).exclude(id=equipment_id).select_related('owner')[:4]
    
    context = {
        'equipment': equipment,
        'similar_equipment': similar_equipment,
        'is_available': equipment.availability and not active_booking
    }
    return render(request, 'equipment/detail.html', context)