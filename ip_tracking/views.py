from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited
import json
from .models import RequestLog


def test_view(request):
    """
    Simple test view to verify the middleware is working.
    """
    return JsonResponse({
        'message': 'IP tracking is working!',
        'your_ip': request.META.get('REMOTE_ADDR', 'Unknown')
    })


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@csrf_exempt
@require_http_methods(["POST"])
def sensitive_login_view(request):
    """
    Rate-limited login view for anonymous users.
    5 requests per minute for unauthenticated users.
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'error': 'Username and password required'
            }, status=400)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user': username
            })
        else:
            return JsonResponse({
                'error': 'Invalid credentials'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Login failed'
        }, status=500)


@ratelimit(key='ip', rate='10/m', method=['GET', 'POST'], block=True)
@login_required
def authenticated_api_view(request):
    """
    Rate-limited API view for authenticated users.
    10 requests per minute for authenticated users.
    """
    return JsonResponse({
        'message': 'You have access to the authenticated API!',
        'user': request.user.username,
        'requests_remaining': 'Rate limit: 10/minute for authenticated users'
    })


@ratelimit(key='ip', rate='3/m', method='GET', block=True)
def admin_sensitive_view(request):
    """
    Highly rate-limited view for admin-like sensitive operations.
    3 requests per minute.
    """
    return JsonResponse({
        'message': 'This is a sensitive admin endpoint',
        'warning': 'This endpoint is heavily rate limited (3/minute)'
    })


def rate_limit_exceeded_view(request, exception):
    """
    Custom view for when rate limit is exceeded.
    """
    return JsonResponse({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.',
        'details': 'Rate limiting is in effect to prevent abuse.'
    }, status=429)


def ip_stats_view(request):
    """
    View to show IP statistics (not rate limited for testing).
    """
    # Get stats for the requesting IP
    client_ip = request.META.get('REMOTE_ADDR', 'Unknown')
    
    # Count requests from this IP in the last hour
    from django.utils import timezone
    from datetime import timedelta
    
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_requests = RequestLog.objects.filter(
        ip_address=client_ip,
        timestamp__gte=one_hour_ago
    ).count()
    
    # Get total requests from this IP
    total_requests = RequestLog.objects.filter(ip_address=client_ip).count()
    
    # Get most recent request details
    latest_request = RequestLog.objects.filter(ip_address=client_ip).first()
    
    return JsonResponse({
        'your_ip': client_ip,
        'requests_last_hour': recent_requests,
        'total_requests': total_requests,
        'latest_request': {
            'path': latest_request.path if latest_request else None,
            'timestamp': latest_request.timestamp.isoformat() if latest_request else None,
            'location': f"{latest_request.city}, {latest_request.country}" if latest_request and latest_request.city else 'Unknown'
        } if latest_request else None
    })
