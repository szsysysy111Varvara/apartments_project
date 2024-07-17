from django.db import models
from django.contrib.auth.models import User
from users.models import Profile


class Listing(models.Model):
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
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class ModelToProfile(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='related_profile')

