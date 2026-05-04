import random
from django.utils import timezone
from .models import Cat, CatOfTheDay

def get_or_create_cat_of_the_day():
    today = timezone.now().date()

    featured = CatOfTheDay.objects.filter(date=today).first()
    if featured:
        return featured.cat

    cat_ids = Cat.objects.values_list('id', flat=True)
    if not cat_ids:
        return None

    random_cat_id = random.choice(cat_ids)
    selected_cat = Cat.objects.get(id=random_cat_id)

    CatOfTheDay.objects.create(cat=selected_cat, date=today)
    return selected_cat