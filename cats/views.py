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

    @action(detail=False, methods=['get'], url_path='weekly_top', permission_classes=[permissions.AllowAny])
    def weekly_top(self, request):
        last_week = timezone.now().date() - timedelta(days=7)
        top_data = DailyCatTop.objects.filter(date__gte=last_week).order_by('-score')[:10]
        serializer = DailyTopSerializer(top_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        """Метод для голосования за кота."""
        cat = self.get_object()
        today = timezone.now().date()

        # Правило 1: Запрет голосования за своего кота
        if cat.owner == request.user:
            return Response({"detail": "За своего кота голосовать нельзя!"}, 
                            status=status.HTTP_400_BAD_REQUEST)
                            
        # Правило 2: Запрет повторного голосования
        if Vote.objects.filter(user=request.user, cat=cat, date=today).exists():
            return Response({"detail": "Вы уже голосовали за этого кота сегодня."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        Vote.objects.create(user=request.user, cat=cat)
        self.update_daily_score(cat.id)
        return Response({"detail": "Голос учтен!"}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_votes(self, request):
        """Список котов, за которых голосовал текущий пользователь."""
        votes = Vote.objects.filter(user=request.user).select_related('cat')
        cats = [vote.cat for vote in votes]
        serializer = self.get_serializer(cats, many=True)
        return Response(serializer.data)
    def update_daily_score(self, cat_id):
        """Вспомогательный метод для обновления баллов в дневном топе."""
        today = timezone.now().date()
        try:
            # Ищем, есть ли уже запись топа на сегодня
            daily_top = DailyCatTop.objects.filter(date=today).first()
            if daily_top:
                # Если кот совпадает, плюсуем балл
                if daily_top.cat_id == cat_id:
                    daily_top.score += 1
                    daily_top.save()
            else:
                # Если на сегодня топа еще нет, создаем
                DailyCatTop.objects.create(date=today, cat_id=cat_id, score=1)
        except Exception:
            # Гасим возможные ошибки базы данных, чтобы голосование не падало
            pass