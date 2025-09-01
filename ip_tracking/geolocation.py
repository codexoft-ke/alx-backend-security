import requests
import logging
from django.core.cache import cache
from django.conf import settings
from ipaddress import ip_address, AddressValueError
import json


logger = logging.getLogger(__name__)


class GeolocationService:
    """
    Service for IP geolocation using multiple providers.
    """
    
    def __init__(self):
        self.cache_timeout = 24 * 60 * 60  # 24 hours
        
    def get_location_data(self, ip_addr):
        """
        Get geolocation data for an IP address.
        
        Args:
            ip_addr (str): IP address to geolocate
            
        Returns:
            dict: Location data with keys: country, city, region, latitude, longitude
        """
        # Check if IP is private/local
        if self._is_private_ip(ip_addr):
            return self._get_default_location_data()
        
        # Check cache first
        cache_key = f"geo_{ip_addr}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        # Try to get fresh data from API
        location_data = self._fetch_from_api(ip_addr)
        
        # Cache the result
        cache.set(cache_key, location_data, self.cache_timeout)
        
        return location_data
    
    def _is_private_ip(self, ip_addr):
        """Check if IP address is private/local."""
        try:
            ip_obj = ip_address(ip_addr)
            return ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local
        except AddressValueError:
            return True
    
    def _get_default_location_data(self):
        """Return default location data for private/local IPs."""
        return {
            'country': 'Local',
            'city': 'Local',
            'region': 'Local',
            'latitude': None,
            'longitude': None
        }
    
    def _fetch_from_api(self, ip_addr):
        """
        Fetch geolocation data from API.
        
        Uses ipapi.co as the primary provider (free tier: 1000 requests/day)
        """
        try:
            # Try ipapi.co first (free service)
            response = requests.get(
                f"http://ipapi.co/{ip_addr}/json/",
                timeout=5,
                headers={'User-Agent': 'IP-Tracking-Django-App'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we got valid data
                if 'error' not in data and data.get('country_name'):
                    return {
                        'country': data.get('country_name', ''),
                        'city': data.get('city', ''),
                        'region': data.get('region', ''),
                        'latitude': data.get('latitude'),
                        'longitude': data.get('longitude')
                    }
            
        except Exception as e:
            logger.warning(f"Failed to get geolocation for {ip_addr} from ipapi.co: {e}")
        
        # Try fallback API (ip-api.com - free tier: 1000 requests/minute)
        try:
            response = requests.get(
                f"http://ip-api.com/json/{ip_addr}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    return {
                        'country': data.get('country', ''),
                        'city': data.get('city', ''),
                        'region': data.get('regionName', ''),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon')
                    }
                    
        except Exception as e:
            logger.warning(f"Failed to get geolocation for {ip_addr} from ip-api.com: {e}")
        
        # Return empty data if all APIs fail
        logger.warning(f"Could not get geolocation data for {ip_addr}")
        return {
            'country': '',
            'city': '',
            'region': '',
            'latitude': None,
            'longitude': None
        }


# Global instance
geolocation_service = GeolocationService()
