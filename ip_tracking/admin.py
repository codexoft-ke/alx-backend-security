from django.contrib import admin
from django.core.cache import cache
from .models import RequestLog, BlockedIP, SuspiciousIP


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing request logs.
    """
    list_display = ('ip_address', 'path', 'country', 'city', 'timestamp')
    list_filter = ('timestamp', 'country', 'city')
    search_fields = ('ip_address', 'path', 'country', 'city')
    readonly_fields = ('ip_address', 'path', 'timestamp', 'country', 'city', 'region', 'latitude', 'longitude')
    ordering = ('-timestamp',)
    
    # Make the admin read-only since these are logs
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    """
    Admin interface for managing blocked IPs.
    """
    list_display = ('ip_address', 'reason', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('ip_address', 'reason')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def save_model(self, request, obj, form, change):
        """Clear cache when blocking/unblocking IPs."""
        super().save_model(request, obj, form, change)
        # Clear cache for this IP
        cache.delete(f"blocked_ip_{obj.ip_address}")
    
    def delete_model(self, request, obj):
        """Clear cache when deleting blocked IP."""
        cache.delete(f"blocked_ip_{obj.ip_address}")
        super().delete_model(request, obj)


@admin.register(SuspiciousIP)
class SuspiciousIPAdmin(admin.ModelAdmin):
    """
    Admin interface for managing suspicious IPs.
    """
    list_display = ('ip_address', 'reason', 'severity', 'request_count', 'is_resolved', 'flagged_at')
    list_filter = ('severity', 'is_resolved', 'flagged_at')
    search_fields = ('ip_address', 'reason')
    readonly_fields = ('flagged_at',)
    ordering = ('-flagged_at',)
    
    actions = ['mark_as_resolved', 'block_suspicious_ips']
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected suspicious IPs as resolved."""
        updated = queryset.update(is_resolved=True)
        self.message_user(request, f'{updated} suspicious IP(s) marked as resolved.')
    mark_as_resolved.short_description = "Mark selected IPs as resolved"
    
    def block_suspicious_ips(self, request, queryset):
        """Block selected suspicious IPs."""
        blocked_count = 0
        for suspicious_ip in queryset:
            if not BlockedIP.objects.filter(ip_address=suspicious_ip.ip_address, is_active=True).exists():
                BlockedIP.objects.create(
                    ip_address=suspicious_ip.ip_address,
                    reason=f"Blocked from admin: {suspicious_ip.reason}",
                    is_active=True
                )
                blocked_count += 1
                # Clear cache
                cache.delete(f"blocked_ip_{suspicious_ip.ip_address}")
        
        self.message_user(request, f'{blocked_count} suspicious IP(s) have been blocked.')
    block_suspicious_ips.short_description = "Block selected suspicious IPs"
