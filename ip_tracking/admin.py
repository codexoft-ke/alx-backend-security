from django.contrib import admin
from .models import RequestLog


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing request logs.
    """
    list_display = ('ip_address', 'path', 'timestamp')
    list_filter = ('timestamp', 'ip_address')
    search_fields = ('ip_address', 'path')
    readonly_fields = ('ip_address', 'path', 'timestamp')
    ordering = ('-timestamp',)
    
    # Make the admin read-only since these are logs
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
