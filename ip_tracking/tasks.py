from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from collections import defaultdict
import logging
from .models import RequestLog, SuspiciousIP, BlockedIP

logger = logging.getLogger(__name__)


@shared_task
def detect_anomalies():
    """
    Celery task to detect anomalous IP behavior.
    
    This task runs hourly and checks for:
    1. IPs with excessive request volume (>100 requests/hour)
    2. IPs accessing sensitive paths repeatedly
    3. IPs with unusual geographic patterns
    """
    logger.info("Starting anomaly detection task...")
    
    # Get the time window (last hour)
    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)
    
    # Get requests from the last hour
    recent_requests = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago
    ).select_related()
    
    # Track statistics
    flagged_ips = []
    
    # 1. Check for high volume IPs
    flagged_ips.extend(check_high_volume_ips(recent_requests))
    
    # 2. Check for sensitive path access
    flagged_ips.extend(check_sensitive_path_access(recent_requests))
    
    # 3. Check for rapid fire requests
    flagged_ips.extend(check_rapid_fire_requests(recent_requests))
    
    # 4. Check for geographic anomalies
    flagged_ips.extend(check_geographic_anomalies(recent_requests))
    
    # Process flagged IPs
    total_flagged = process_flagged_ips(flagged_ips)
    
    logger.info(f"Anomaly detection completed. Flagged {total_flagged} suspicious activities.")
    
    return {
        'total_requests_analyzed': recent_requests.count(),
        'suspicious_activities_flagged': total_flagged,
        'timestamp': now.isoformat()
    }


def check_high_volume_ips(requests_queryset):
    """Check for IPs with excessive request volume."""
    flagged = []
    
    # Group requests by IP and count
    ip_counts = requests_queryset.values('ip_address').annotate(
        request_count=Count('id')
    ).filter(request_count__gt=100)  # More than 100 requests per hour
    
    for ip_data in ip_counts:
        flagged.append({
            'ip_address': ip_data['ip_address'],
            'reason': f"Excessive requests: {ip_data['request_count']} requests/hour",
            'severity': 'high' if ip_data['request_count'] > 500 else 'medium',
            'request_count': ip_data['request_count']
        })
    
    return flagged


def check_sensitive_path_access(requests_queryset):
    """Check for repeated access to sensitive paths."""
    flagged = []
    
    # Define sensitive paths
    sensitive_paths = [
        '/admin',
        '/login',
        '/api/auth',
        '/wp-admin',
        '/.env',
        '/config',
        '/database',
        '/.git',
        '/backup'
    ]
    
    # Check each IP for sensitive path access
    for ip in requests_queryset.values_list('ip_address', flat=True).distinct():
        sensitive_requests = requests_queryset.filter(
            ip_address=ip
        ).filter(
            path__icontains='/admin'
        ).union(
            requests_queryset.filter(ip_address=ip, path__icontains='/login')
        ).union(
            requests_queryset.filter(ip_address=ip, path__icontains='/.env')
        ).union(
            requests_queryset.filter(ip_address=ip, path__icontains='/wp-admin')
        ).union(
            requests_queryset.filter(ip_address=ip, path__icontains='/.git')
        )
        
        sensitive_count = sensitive_requests.count()
        
        if sensitive_count >= 5:  # 5 or more sensitive path accesses
            flagged.append({
                'ip_address': ip,
                'reason': f"Multiple sensitive path access: {sensitive_count} attempts",
                'severity': 'high' if sensitive_count > 20 else 'medium',
                'request_count': sensitive_count
            })
    
    return flagged


def check_rapid_fire_requests(requests_queryset):
    """Check for rapid fire requests (too many requests in short time)."""
    flagged = []
    
    # Group requests by IP and check for rapid patterns
    for ip in requests_queryset.values_list('ip_address', flat=True).distinct():
        ip_requests = requests_queryset.filter(ip_address=ip).order_by('timestamp')
        
        if ip_requests.count() < 10:  # Skip IPs with few requests
            continue
        
        # Check for bursts: more than 20 requests in any 5-minute window
        five_minutes = timedelta(minutes=5)
        
        for i, request in enumerate(ip_requests):
            window_start = request.timestamp
            window_end = window_start + five_minutes
            
            window_requests = ip_requests.filter(
                timestamp__gte=window_start,
                timestamp__lt=window_end
            ).count()
            
            if window_requests > 20:  # More than 20 requests in 5 minutes
                flagged.append({
                    'ip_address': ip,
                    'reason': f"Rapid fire requests: {window_requests} requests in 5 minutes",
                    'severity': 'medium',
                    'request_count': window_requests
                })
                break  # Only flag once per IP
    
    return flagged


def check_geographic_anomalies(requests_queryset):
    """Check for geographic anomalies (requests from multiple countries)."""
    flagged = []
    
    # Group by IP and check for multiple countries
    for ip in requests_queryset.values_list('ip_address', flat=True).distinct():
        countries = requests_queryset.filter(
            ip_address=ip
        ).exclude(
            country__in=['', 'Local']
        ).values_list('country', flat=True).distinct()
        
        if len(countries) > 1:  # Requests from multiple countries
            flagged.append({
                'ip_address': ip,
                'reason': f"Geographic anomaly: requests from {len(countries)} different countries",
                'severity': 'low',
                'request_count': requests_queryset.filter(ip_address=ip).count()
            })
    
    return flagged


def process_flagged_ips(flagged_ips):
    """Process and store flagged IPs."""
    total_flagged = 0
    
    for flag_data in flagged_ips:
        # Check if this IP + reason combination was already flagged recently
        recent_flag = SuspiciousIP.objects.filter(
            ip_address=flag_data['ip_address'],
            reason=flag_data['reason'],
            flagged_at__gte=timezone.now() - timedelta(hours=6)
        ).exists()
        
        if not recent_flag:
            # Create new suspicious IP record
            SuspiciousIP.objects.create(
                ip_address=flag_data['ip_address'],
                reason=flag_data['reason'],
                severity=flag_data['severity'],
                request_count=flag_data['request_count']
            )
            total_flagged += 1
            
            logger.warning(
                f"Flagged suspicious IP: {flag_data['ip_address']} - "
                f"{flag_data['reason']} (Severity: {flag_data['severity']})"
            )
            
            # Auto-block critical severity IPs
            if flag_data['severity'] == 'critical':
                auto_block_ip(flag_data)
    
    return total_flagged


def auto_block_ip(flag_data):
    """Automatically block IPs with critical severity flags."""
    ip_address = flag_data['ip_address']
    
    # Check if IP is already blocked
    if not BlockedIP.objects.filter(ip_address=ip_address, is_active=True).exists():
        BlockedIP.objects.create(
            ip_address=ip_address,
            reason=f"Auto-blocked: {flag_data['reason']}",
            is_active=True
        )
        
        logger.critical(f"Auto-blocked critical threat IP: {ip_address}")


@shared_task
def cleanup_old_logs():
    """
    Clean up old request logs to prevent database bloat.
    Runs daily and removes logs older than 30 days.
    """
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Delete old request logs
    deleted_count, _ = RequestLog.objects.filter(
        timestamp__lt=thirty_days_ago
    ).delete()
    
    logger.info(f"Cleaned up {deleted_count} old request logs")
    
    return {
        'deleted_logs': deleted_count,
        'cutoff_date': thirty_days_ago.isoformat()
    }


@shared_task
def generate_security_report():
    """
    Generate a daily security report.
    """
    now = timezone.now()
    yesterday = now - timedelta(days=1)
    
    # Get statistics
    total_requests = RequestLog.objects.filter(timestamp__gte=yesterday).count()
    unique_ips = RequestLog.objects.filter(timestamp__gte=yesterday).values('ip_address').distinct().count()
    blocked_ips = BlockedIP.objects.filter(is_active=True).count()
    suspicious_flags = SuspiciousIP.objects.filter(flagged_at__gte=yesterday).count()
    
    # Top countries
    top_countries = RequestLog.objects.filter(
        timestamp__gte=yesterday
    ).exclude(
        country=''
    ).values('country').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    report = {
        'date': yesterday.date().isoformat(),
        'total_requests': total_requests,
        'unique_ips': unique_ips,
        'blocked_ips': blocked_ips,
        'suspicious_flags': suspicious_flags,
        'top_countries': list(top_countries)
    }
    
    logger.info(f"Security report generated: {report}")
    
    return report
