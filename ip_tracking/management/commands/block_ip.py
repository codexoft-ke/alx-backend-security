from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from ip_tracking.models import BlockedIP
from ipaddress import ip_address, ip_network, AddressValueError
import sys


class Command(BaseCommand):
    help = 'Block IP addresses from accessing the application'

    def add_arguments(self, parser):
        parser.add_argument(
            'ip_address',
            type=str,
            help='IP address or CIDR network to block (e.g., 192.168.1.1 or 192.168.1.0/24)'
        )
        parser.add_argument(
            '--reason',
            type=str,
            default='Manual block',
            help='Reason for blocking this IP address'
        )
        parser.add_argument(
            '--unblock',
            action='store_true',
            help='Unblock the specified IP address instead of blocking it'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all currently blocked IPs'
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_blocked_ips()
            return

        ip_input = options['ip_address']
        reason = options['reason']
        unblock = options['unblock']

        try:
            # Validate IP address or network
            try:
                # Try as single IP first
                ip_obj = ip_address(ip_input)
                ip_addresses = [str(ip_obj)]
            except AddressValueError:
                # Try as network
                try:
                    network = ip_network(ip_input, strict=False)
                    ip_addresses = [str(ip) for ip in network.hosts()]
                    if len(ip_addresses) > 1000:
                        raise CommandError(
                            f"Network {ip_input} is too large (>1000 hosts). "
                            "Please use smaller subnets for security."
                        )
                except AddressValueError:
                    raise CommandError(f"Invalid IP address or network: {ip_input}")

            if unblock:
                self.unblock_ips(ip_addresses)
            else:
                self.block_ips(ip_addresses, reason)

        except Exception as e:
            raise CommandError(f"Error processing IP {ip_input}: {str(e)}")

    def block_ips(self, ip_addresses, reason):
        """Block a list of IP addresses."""
        blocked_count = 0
        already_blocked = 0

        for ip_addr in ip_addresses:
            blocked_ip, created = BlockedIP.objects.get_or_create(
                ip_address=ip_addr,
                defaults={
                    'reason': reason,
                    'is_active': True
                }
            )

            if created:
                blocked_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Blocked IP: {ip_addr} - {reason}")
                )
                # Clear cache for this IP
                cache.delete(f"blocked_ip_{ip_addr}")
            else:
                if not blocked_ip.is_active:
                    # Reactivate existing block
                    blocked_ip.is_active = True
                    blocked_ip.reason = reason
                    blocked_ip.save()
                    blocked_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Reactivated block for IP: {ip_addr}")
                    )
                    cache.delete(f"blocked_ip_{ip_addr}")
                else:
                    already_blocked += 1
                    self.stdout.write(
                        self.style.WARNING(f"⚠ IP already blocked: {ip_addr}")
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSummary: {blocked_count} IPs blocked, {already_blocked} already blocked"
            )
        )

    def unblock_ips(self, ip_addresses):
        """Unblock a list of IP addresses."""
        unblocked_count = 0
        not_blocked = 0

        for ip_addr in ip_addresses:
            try:
                blocked_ip = BlockedIP.objects.get(ip_address=ip_addr, is_active=True)
                blocked_ip.is_active = False
                blocked_ip.save()
                unblocked_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Unblocked IP: {ip_addr}")
                )
                # Clear cache for this IP
                cache.delete(f"blocked_ip_{ip_addr}")
            except BlockedIP.DoesNotExist:
                not_blocked += 1
                self.stdout.write(
                    self.style.WARNING(f"⚠ IP not blocked: {ip_addr}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSummary: {unblocked_count} IPs unblocked, {not_blocked} were not blocked"
            )
        )

    def list_blocked_ips(self):
        """List all currently blocked IPs."""
        blocked_ips = BlockedIP.objects.filter(is_active=True).order_by('-created_at')
        
        if not blocked_ips.exists():
            self.stdout.write(self.style.WARNING("No IPs are currently blocked."))
            return

        self.stdout.write(self.style.SUCCESS(f"\nCurrently blocked IPs ({blocked_ips.count()}):"))
        self.stdout.write("-" * 80)
        
        for blocked_ip in blocked_ips:
            self.stdout.write(
                f"{blocked_ip.ip_address:<20} | {blocked_ip.reason:<30} | {blocked_ip.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        
        self.stdout.write("-" * 80)
