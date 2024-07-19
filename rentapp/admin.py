from django.contrib import admin

from rentapp.models import Listing, Review
from rentapp.models import Booking


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('listing', 'owner', 'rating', 'created_at')
    search_fields = ('owner__username', 'listing__id')


class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'owner', 'renter', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('listing__name', 'owner__username', 'renter__username')
    date_hierarchy = 'start_date'

class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'price', 'availability')
    list_filter = ('availability',)
    search_fields = ('name', 'owner__username')
    date_hierarchy = 'created_at'

admin.site.register(Listing)
admin.site.register(Booking)
