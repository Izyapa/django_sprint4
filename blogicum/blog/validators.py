from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.timesince import timesince


def age_protect(value):
    """Валидатор проверки возраста."""
    age = timesince(value, timezone.now())
    age_years = int(age.split()[0])
    if age_years > 200:
        raise ValidationError('Запись не может быть старше 200 лет!')
