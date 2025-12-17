from django.shortcuts import render
from equipment.models import Equipment

def home(request):
    # Get featured equipment (recently added, available)
    featured_equipment = Equipment.objects.filter(
        availability=True
    ).select_related('owner').order_by('-created_at')[:6]
    
    context = {
        'featured_equipment': featured_equipment
    }
    return render(request, 'pages/home.html', context)

def about(request):
    context = {
        'title': 'About GreenGear',
        'description': 'GreenGear is a platform connecting farmers with equipment owners for sustainable agriculture.'
    }
    return render(request, 'pages/about.html', context)

def services(request):
    context = {
        'title': 'Our Services',
        'services': [
            'Equipment Rental',
            'Farm Management',
            'Maintenance Support',
            'Delivery Services'
        ]
    }
    return render(request, 'pages/services.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you would typically save to database or send email
        # For now, we'll just show a success message
        
        # Example email sending (uncomment when email is configured)
        """
        send_mail(
            f'GreenGear Contact: {subject}',
            f'Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}',
            email,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        """
        
        messages.success(request, 'Thank you for your message! We will get back to you within 24 hours.')
        return redirect('contact')
    
    context = {
        'title': 'Contact Us',
        'contact_info': {
            'phone': '+91 98765 43210',
            'email': 'support@greengear.com',
            'address': '123 Farm Street, Agriculture City'
        }
    }
    return render(request, 'pages/contact.html', context)