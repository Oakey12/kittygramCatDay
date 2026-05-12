from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Breed(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название породы')

    class Meta:
        verbose_name = 'Порода'
        verbose_name_plural = 'Породы'

    def __str__(self):
        return self.name

class Cat(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя')
    color = models.CharField(max_length=100, verbose_name='Цвет')
    birth_year = models.IntegerField(verbose_name='Год рождения')

    breed = models.ForeignKey(Breed, on_delete=models.SET_NULL, null=True, verbose_name='Порода')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cats', verbose_name='Владелец')

    class Meta:
        verbose_name = 'Кот'
        verbose_name_plural = 'Коты'

    def __str__(self):
        return self.name

class CatOfTheDay(models.Model):
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, related_name='featured_days', verbose_name='Кот')
    date = models.DateField(default=timezone.now, unique=True, verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Кот дня'
        verbose_name_plural = 'Коты дня'
        ordering = ['-date']

    def __str__(self):
        return f"Кот дня на {self.date}: {self.cat.name}"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    cat = models.ForeignKey('Cat', on_delete=models.CASCADE, related_name='votes')
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'cat', 'date')
    

class DailyCatTop(models.Model):
    date = models.DateField(unique=True, default=timezone.now)
    cat = models.ForeignKey('Cat', on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Дневной топ'
        ordering = ['-date', '-score']