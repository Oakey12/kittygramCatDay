from rest_framework import serializers
from django.utils import timezone
from .models import Cat, Breed

class BreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = '__all__'

class CatSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Cat
        fields = ['id', 'name', 'color', 'birth_year', 'breed', 'owner']

    def validate_birth_year(self, value):
        current_year = timezone.now().year
        if value > current_year:
            raise serializers.ValidationError("Год рождения не может быть в будущем.")
        if value < 1990:
            raise serializers.ValidationError("Укажите корректный год рождения.")
        return value