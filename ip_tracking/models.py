from django.db import models
from django.utils import timezone


class RequestLog(models.Model):
    """
    Model to store request logging information.
    Tracks IP address, timestamp, and path for each incoming request.
    """
    ip_address = models.GenericIPAddressField(
        help_text="IP address of the client making the request"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when the request was made"
    )
    path = models.CharField(
        max_length=255,
        help_text="URL path that was requested"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Country of the client based on IP geolocation"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="City of the client based on IP geolocation"
    )
    region = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Region/State of the client based on IP geolocation"
    )
    latitude = models.FloatField(
        blank=True,
        null=True,
        help_text="Latitude coordinate"
    )
    longitude = models.FloatField(
        blank=True,
        null=True,
        help_text="Longitude coordinate"
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Request Log"
        verbose_name_plural = "Request Logs"

    def __str__(self):
        location = f"{self.city}, {self.country}" if self.city and self.country else "Unknown location"
        return f"{self.ip_address} ({location}) - {self.path} at {self.timestamp}"


class BlockedIP(models.Model):
    """
    Model to store blocked IP addresses.
    """
    ip_address = models.GenericIPAddressField(
        unique=True,
        help_text="IP address to block from accessing the application"
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Reason for blocking this IP address"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When this IP was blocked"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this block is currently active"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Blocked IP"
        verbose_name_plural = "Blocked IPs"

    def __str__(self):
        return f"Blocked: {self.ip_address} - {self.reason}"


class SuspiciousIP(models.Model):
    """
    Model to store IPs flagged as suspicious by anomaly detection.
    """
    ip_address = models.GenericIPAddressField(
        help_text="IP address flagged as suspicious"
    )
    reason = models.CharField(
        max_length=255,
        help_text="Reason why this IP was flagged as suspicious"
    )
    flagged_at = models.DateTimeField(
        default=timezone.now,
        help_text="When this IP was flagged"
    )
    request_count = models.IntegerField(
        default=0,
        help_text="Number of requests that triggered the flag"
    )
    severity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='medium',
        help_text="Severity level of the suspicious activity"
    )
    is_resolved = models.BooleanField(
        default=False,
        help_text="Whether this suspicious activity has been resolved"
    )
    
    class Meta:
        ordering = ['-flagged_at']
        verbose_name = "Suspicious IP"
        verbose_name_plural = "Suspicious IPs"
        unique_together = ['ip_address', 'reason', 'flagged_at']

    def __str__(self):
        return f"Suspicious: {self.ip_address} - {self.reason} ({self.severity})"
