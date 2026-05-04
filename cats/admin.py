from django.contrib import admin
from .models import Cat, Breed, CatOfTheDay

@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'birth_year', 'breed', 'owner')
    list_filter = ('breed', 'birth_year')

@admin.register(CatOfTheDay)
class CatOfTheDayAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'cat')
    list_filter = ('date',)