from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cat, Breed
from .serializers import CatSerializer, BreedSerializer
from .permissions import IsOwnerOrReadOnly
from .services import get_or_create_cat_of_the_day

class BreedViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer
    permission_classes = [permissions.AllowAny]

class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'], url_path='cat_of_the_day', permission_classes=[permissions.AllowAny])
    def cat_of_the_day(self, request):
        cat = get_or_create_cat_of_the_day()
        if not cat:
            return Response({"detail": "В базе пока нет ни одного кота."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(cat)
        return Response(serializer.data, status=status.HTTP_200_OK)