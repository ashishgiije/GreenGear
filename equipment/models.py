from django.db import models
from django.conf import settings
import os

def equipment_image_path(instance, filename):
    return f'equipment_photos/user_{instance.owner.id}/{filename}'

class Equipment(models.Model):
    CATEGORY_CHOICES = (
        ('tractor', 'Tractor'),
        ('sprayer', 'Sprayer'),
        ('rotavator', 'Rotavator'),
        ('harvester', 'Harvester'),
        ('irrigation', 'Irrigation'),
        ('other', 'Other'),
    )
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='equipment')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    rent_per_day = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rent_per_hour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=100)
    availability = models.BooleanField(default=True)
    image = models.ImageField(upload_to=equipment_image_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)

    class Meta:
        db_table = 'equipment_equipment'
        ordering = ['-created_at']