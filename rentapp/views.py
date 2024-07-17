from rest_framework import viewsets, permissions
from .models import Listing
from .serializers import ListingSerializer
from .permissions import IsRenter, IsLandlord

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsLandlord()]
        else:
            return [permissions.IsAuthenticated(), IsRenter()]

