from django.conf import settings
from django.shortcuts import render


def index(request):
    return render(request, 'lands/index.html', {'base_url': settings.BASE_URL})
