from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from unittest.mock import patch
from .middleware import IPTrackingMiddleware
from .models import RequestLog


class IPTrackingMiddlewareTest(TestCase):
    """
    Test cases for the IP tracking middleware.
    """
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = IPTrackingMiddleware(lambda request: None)
    
    def test_get_client_ip_with_x_forwarded_for(self):
        """Test IP extraction from X-Forwarded-For header."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        
        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
    
    def test_get_client_ip_with_x_real_ip(self):
        """Test IP extraction from X-Real-IP header."""
        request = self.factory.get('/')
        request.META['HTTP_X_REAL_IP'] = '192.168.1.2'
        
        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.2')
    
    def test_get_client_ip_with_remote_addr(self):
        """Test IP extraction from REMOTE_ADDR."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.3'
        
        ip = self.middleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.3')
    
    def test_get_client_ip_fallback(self):
        """Test IP fallback when no headers are present."""
        request = self.factory.get('/')
        
        ip = self.middleware.get_client_ip(request)
        # RequestFactory sets REMOTE_ADDR to 127.0.0.1 by default
        self.assertEqual(ip, '127.0.0.1')


class RequestLogModelTest(TestCase):
    """
    Test cases for the RequestLog model.
    """
    
    def test_request_log_creation(self):
        """Test creating a RequestLog instance."""
        log = RequestLog.objects.create(
            ip_address='192.168.1.1',
            path='/test-path/'
        )
        
        self.assertEqual(log.ip_address, '192.168.1.1')
        self.assertEqual(log.path, '/test-path/')
        self.assertIsNotNone(log.timestamp)
    
    def test_request_log_str_representation(self):
        """Test the string representation of RequestLog."""
        log = RequestLog.objects.create(
            ip_address='192.168.1.1',
            path='/test-path/'
        )
        
        expected = f"192.168.1.1 - /test-path/ at {log.timestamp}"
        self.assertEqual(str(log), expected)
