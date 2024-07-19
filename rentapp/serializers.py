from rest_framework import serializers
from .models import Listing, Booking


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'location', 'price', 'rooms', 'housing_type', 'status', 'owner']
        read_only_fields = ['owner']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'owner', 'listing', 'start_date', 'end_date', 'status', 'created_at', 'updated_at', 'cancellation_deadline']
        read_only_fields = ['owner', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request:
            validated_data['owner'] = request.user
        return super().create(validated_data)