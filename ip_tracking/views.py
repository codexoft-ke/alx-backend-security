from django.shortcuts import render
from django.http import JsonResponse
from .models import RequestLog


def test_view(request):
    """
    Simple test view to verify the middleware is working.
    """
    return JsonResponse({
        'message': 'IP tracking is working!',
        'your_ip': request.META.get('REMOTE_ADDR', 'Unknown')
    })
