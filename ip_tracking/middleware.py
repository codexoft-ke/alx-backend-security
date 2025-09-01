import logging
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.core.cache import cache
from .models import RequestLog, BlockedIP
from .geolocation import geolocation_service


# Configure logging
logger = logging.getLogger(__name__)


class IPTrackingMiddleware:
    """
    Middleware to log IP address, timestamp, and path of every incoming request.
    
    This middleware captures the client's IP address (handling proxy headers),
    the current timestamp, and the requested path, then stores this information
    in the RequestLog model.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process the request and log the details.
        
        Args:
            request: The HTTP request object
            
        Returns:
            The HTTP response from the next middleware/view
        """
        # Get client IP address
        ip_address = self.get_client_ip(request)
        
        # Check if IP is blocked
        if self.is_ip_blocked(ip_address):
            logger.warning(f"Blocked request from {ip_address} to {request.get_full_path()}")
            return HttpResponseForbidden("Access denied: Your IP address has been blocked.")
        
        # Get request path
        path = request.get_full_path()
        
        # Get current timestamp
        timestamp = timezone.now()
        
        # Log the request details
        try:
            # Get geolocation data
            location_data = geolocation_service.get_location_data(ip_address)
            
            RequestLog.objects.create(
                ip_address=ip_address,
                timestamp=timestamp,
                path=path,
                country=location_data['country'],
                city=location_data['city'],
                region=location_data['region'],
                latitude=location_data['latitude'],
                longitude=location_data['longitude']
            )
            logger.info(f"Logged request: {ip_address} ({location_data['city']}, {location_data['country']}) - {path} at {timestamp}")
        except Exception as e:
            # Log error but don't break the request processing
            logger.error(f"Failed to log request: {e}")
        
        # Continue processing the request
        response = self.get_response(request)
        
        return response
    
    def is_ip_blocked(self, ip_address):
        """
        Check if an IP address is blocked.
        
        Uses caching to avoid database hits on every request.
        
        Args:
            ip_address: The IP address to check
            
        Returns:
            bool: True if the IP is blocked, False otherwise
        """
        cache_key = f"blocked_ip_{ip_address}"
        is_blocked = cache.get(cache_key)
        
        if is_blocked is None:
            # Check database
            is_blocked = BlockedIP.objects.filter(
                ip_address=ip_address,
                is_active=True
            ).exists()
            
            # Cache result for 5 minutes
            cache.set(cache_key, is_blocked, 300)
        
        return is_blocked
    
    def get_client_ip(self, request):
        """
        Extract the client's IP address from the request.
        
        This method handles various proxy headers to get the real client IP.
        
        Args:
            request: The HTTP request object
            
        Returns:
            str: The client's IP address
        """
        # Check for IP in proxy headers (in order of preference)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            ip = x_forwarded_for.split(',')[0].strip()
            return ip
        
        # Check for real IP header (used by some proxies)
        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip:
            return x_real_ip.strip()
        
        # Check for client IP header
        x_client_ip = request.META.get('HTTP_X_CLIENT_IP')
        if x_client_ip:
            return x_client_ip.strip()
        
        # Fall back to remote address
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
