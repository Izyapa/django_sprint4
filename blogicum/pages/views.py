from django.shortcuts import render
from django.views.generic import TemplateView


class About(TemplateView):
    """Вывод информации."""

    template_name = 'pages/about.html'


class Rules(TemplateView):
    """Вывод правил."""

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Ошибка 404."""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Ошибка 403."""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """Ошибка 500."""
    return render(request, 'pages/500.html', status=500)
