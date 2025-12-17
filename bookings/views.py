from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import date, datetime  # Add this import
from .models import Booking
from equipment.models import Equipment

@login_required
def booking_create(request, equipment_id):
    if request.user.role != 'farmer':
        messages.error(request, 'Only farmers can book equipment.')
        return redirect('home')
    
    equipment = get_object_or_404(Equipment, id=equipment_id)
    
    # Check if equipment is available
    if not equipment.availability:
        messages.error(request, 'This equipment is currently not available for booking.')
        return redirect('equipment:detail', equipment_id=equipment_id)
    
    # Check for active bookings
    active_booking = Booking.objects.filter(
        equipment=equipment,
        status__in=['pending', 'approved']
    ).exists()
    
    if active_booking:
        messages.error(request, 'This equipment is currently booked by another farmer.')
        return redirect('equipment:detail', equipment_id=equipment_id)
    
    # Set minimum date to today
    min_date = date.today().isoformat()
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        duration = request.POST.get('duration')
        duration_type = request.POST.get('duration_type')
        
        if not start_date or not duration:
            messages.error(request, 'Please fill all required fields.')
            return redirect('bookings:create', equipment_id=equipment_id)
        
        # Check if start date is in the future
        if start_date < min_date:
            messages.error(request, 'Start date must be in the future.')
            return redirect('bookings:create', equipment_id=equipment_id)
        
        # Check for date conflicts
        existing_booking = Booking.objects.filter(
            equipment=equipment,
            start_date=start_date,
            status__in=['pending', 'approved']
        ).exists()
        
        if existing_booking:
            messages.error(request, 'Equipment is already booked for the selected date.')
            return redirect('bookings:create', equipment_id=equipment_id)
        
        # Calculate total amount
        if duration_type == 'days':
            total_amount = int(duration) * (equipment.rent_per_day or 0)
        else:
            total_amount = int(duration) * (equipment.rent_per_hour or 0)
        
        try:
            booking = Booking.objects.create(
                farmer=request.user,
                equipment=equipment,
                start_date=start_date,
                duration=duration,
                duration_type=duration_type,
                total_amount=total_amount
            )
            messages.success(request, f'Booking request sent! Total amount: ₹{total_amount}. Pay cash on delivery.')
            return redirect('bookings:detail', booking_id=booking.id)
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
    
    context = {
        'equipment': equipment,
        'equipment_id': equipment_id,
        'min_date': min_date
    }
    return render(request, 'bookings/create.html', context)

@login_required
def booking_detail(request, booking_id):
    if request.user.role == 'farmer':
        booking = get_object_or_404(Booking, id=booking_id, farmer=request.user)
    else:
        booking = get_object_or_404(Booking, id=booking_id, equipment__owner=request.user)
    
    context = {
        'booking': booking
    }
    return render(request, 'bookings/detail.html', context)

@login_required
def farmer_bookings(request):
    if request.user.role != 'farmer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    bookings = Booking.objects.filter(farmer=request.user).select_related('equipment', 'equipment__owner').order_by('-created_at')
    
    # Handle status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    context = {
        'bookings': bookings,
        'status_filter': status_filter
    }
    return render(request, 'bookings/farmer_list.html', context)

@login_required
def owner_bookings(request):
    if request.user.role != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    booking_requests = Booking.objects.filter(
        equipment__owner=request.user
    ).select_related('farmer', 'equipment').order_by('-created_at')
    
    # Handle status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        booking_requests = booking_requests.filter(status=status_filter)
    
    context = {
        'booking_requests': booking_requests,
        'status_filter': status_filter
    }
    return render(request, 'bookings/owner_list.html', context)

@login_required
def update_booking_status(request, booking_id, status):
    if request.user.role != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    booking = get_object_or_404(Booking, id=booking_id, equipment__owner=request.user)
    
    valid_statuses = ['approved', 'rejected', 'completed', 'cancelled']
    if status not in valid_statuses:
        messages.error(request, 'Invalid status.')
        return redirect('bookings:owner_list')
    
    # If marking as completed, ensure total_amount is calculated
    if status == 'completed' and not booking.total_amount:
        # Recalculate total amount
        if booking.duration_type == 'days':
            booking.total_amount = booking.duration * (booking.equipment.rent_per_day or 0)
        else:
            booking.total_amount = booking.duration * (booking.equipment.rent_per_hour or 0)
    
    # Update booking status
    old_status = booking.status
    booking.status = status
    booking.save()
    
    status_display = dict(Booking.STATUS_CHOICES).get(status)
    messages.success(request, f'Booking #{booking_id} has been {status_display.lower()}.')
    
    # If completed, show earnings message
    if status == 'completed':
        messages.info(request, f'Earnings of ₹{booking.total_amount} added to your total.')
    
    return redirect('bookings:owner_list')