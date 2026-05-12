from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import Cat, Breed, Vote, DailyCatTop
from .serializers import CatSerializer, BreedSerializer, DailyTopSerializer
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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        """Метод для голосования за кота"""
        cat = self.get_object()
        today = timezone.now().date()

        if Vote.objects.filter(user=request.user, cat=cat, date=today).exists():
            return Response({"detail": "Вы уже голосовали за этого кота сегодня."},
                            status=status.HTTP_400_BAD_REQUEST)

        Vote.objects.create(user=request.user, cat=cat)
        update_daily_score(cat.id)
        return Response({"detail": "Голос учтен!"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='weekly_top', permission_classes=[permissions.AllowAny])
    def weekly_top(self, request):
        """Метод для получения топа за неделю"""
        top_data = get_weekly_top_cats()
        serializer = DailyTopSerializer(top_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

def get_weekly_top_cats():
    last_week = timezone.now().date() - timedelta(days=7)
    return DailyCatTop.objects.filter(date__gte=last_week).order_by('-score')[:10]

def update_daily_score(cat_id):
    today = timezone.now().date()
    votes_count = Vote.objects.filter(cat_id=cat_id, date=today).count()

    obj, created = DailyCatTop.objects.get_or_create(
        date=today,
        defaults={'cat_id': cat_id, 'score': votes_count}
    )
    if not created:
        obj.score = votes_count
        obj.save()