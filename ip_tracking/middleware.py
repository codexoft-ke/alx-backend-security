import logging
from django.utils import timezone
from .models import RequestLog


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
        
        # Get request path
        path = request.get_full_path()
        
        # Get current timestamp
        timestamp = timezone.now()
        
        # Log the request details
        try:
            RequestLog.objects.create(
                ip_address=ip_address,
                timestamp=timestamp,
                path=path
            )
            logger.info(f"Logged request: {ip_address} - {path} at {timestamp}")
        except Exception as e:
            # Log error but don't break the request processing
            logger.error(f"Failed to log request: {e}")
        
        # Continue processing the request
        response = self.get_response(request)
        
        return response
    
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
