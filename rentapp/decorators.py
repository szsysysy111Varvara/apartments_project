from functools import wraps
from django.http import HttpResponseForbidden
from users.models import Profile

def landlord_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and Profile.objects.filter(user=request.user, user_type='Landlord').exists():
            return view_func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("You do not have permission to access this page.")
    return wrapper