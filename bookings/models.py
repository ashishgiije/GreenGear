from django.db import models
from django.conf import settings
from equipment.models import Equipment

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    DURATION_TYPE_CHOICES = (
        ('days', 'Days'),
        ('hours', 'Hours'),
    )
    
    PAYMENT_MODE_CHOICES = (
        ('cash', 'Cash on Delivery'),
    )
    
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    duration = models.IntegerField()
    duration_type = models.CharField(max_length=10, choices=DURATION_TYPE_CHOICES, default='days')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking #{self.id} - {self.equipment.name}"

    def save(self, *args, **kwargs):
        # Calculate total amount if not set
        if not self.total_amount and self.equipment:
            if self.duration_type == 'days':
                self.total_amount = self.duration * (self.equipment.rent_per_day or 0)
            else:
                self.total_amount = self.duration * (self.equipment.rent_per_hour or 0)
        
        # Update equipment availability based on booking status
        if self.status in ['approved', 'pending']:
            self.equipment.availability = False
            self.equipment.save()
        elif self.status in ['completed', 'rejected', 'cancelled']:
            self.equipment.availability = True
            self.equipment.save()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'bookings_booking'
        ordering = ['-created_at']