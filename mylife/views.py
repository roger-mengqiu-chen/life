from django.http import JsonResponse
from django.shortcuts import render

from mylife.services import get_and_save_currency_exchange_rate


def dashboard(request):
    return render(request, 'mylife/dashboard.html')


def get_exchange_rate(request):
    get_and_save_currency_exchange_rate()
    return JsonResponse({'message': 'Currency exchange rates updated successfully.'})
