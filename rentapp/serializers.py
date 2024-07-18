from rest_framework import serializers
from .models import Listing

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'location', 'price', 'rooms', 'type_of_property', 'status', 'owner']
        read_only_fields = ['owner']
