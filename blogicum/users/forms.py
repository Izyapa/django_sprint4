from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# Получаем модель пользователя:
User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """В файле forms.py создаётся собственный класс формы, унаследованный
    от UserCreationForm. Единственное, зачем нужен этот класс — переопределить
    модель, с которой работает форма."""

    # Наследуем класс Meta от соответствующего класса родительской формы.
    # Так этот класс будет не перезаписан, а расширен.
    class Meta(UserCreationForm.Meta):
        """Если класс Meta не наследовать от родительского
        UserCreationForm.Meta,
        то он будет переопределён целиком, а нам этого не нужно: необходимо
        изменить лишь модель, с которой связана форма, а все остальные атрибуты
        этого класса должны унаследоваться от родительского класса."""
        model = User
        fields = ('username', 'bio')
