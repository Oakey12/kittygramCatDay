from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CatViewSet, BreedViewSet

router = DefaultRouter()
router.register('cats', CatViewSet, basename='cats')
router.register('breeds', BreedViewSet, basename='breeds')

urlpatterns = [
    path('', include(router.urls)),
]