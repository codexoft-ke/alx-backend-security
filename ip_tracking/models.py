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

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Request Log"
        verbose_name_plural = "Request Logs"

    def __str__(self):
        return f"{self.ip_address} - {self.path} at {self.timestamp}"
