from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from config import settings
from users.models import Profile


class Listing(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    HOUSING_TYPE_CHOICES = (
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('condo', 'Condo'),
        ('studio', 'Studio'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rooms = models.IntegerField()
    housing_type = models.CharField(max_length=20, choices=HOUSING_TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ModelToProfile(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='related_profile')

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Canceled', 'Canceled'),
        ('Rejected', 'Rejected'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancellation_deadline = models.DateField(default=timezone.now() + timezone.timedelta(days=1))

    def __str__(self):
        return f'Booking {self.id} by {self.owner}'