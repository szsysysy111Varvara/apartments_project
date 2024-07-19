from django.contrib import admin

from users.models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone_number')
    list_filter = ('user_type',)
    search_fields = ('user__username')

admin.site.register(Profile)
