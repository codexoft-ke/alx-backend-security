from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.staticfiles import finders
import os


class Command(BaseCommand):
    help = 'Check static files configuration and locate admin static files'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking static files configuration...'))
        
        # Check settings
        self.stdout.write(f"STATIC_URL: {settings.STATIC_URL}")
        self.stdout.write(f"STATIC_ROOT: {settings.STATIC_ROOT}")
        
        if hasattr(settings, 'STATICFILES_DIRS'):
            self.stdout.write(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
        
        # Check if static root exists
        if os.path.exists(settings.STATIC_ROOT):
            self.stdout.write(self.style.SUCCESS(f"✅ STATIC_ROOT exists: {settings.STATIC_ROOT}"))
            
            # List contents
            static_contents = os.listdir(settings.STATIC_ROOT)
            self.stdout.write(f"Contents: {static_contents}")
            
            # Check for admin static files
            admin_path = os.path.join(settings.STATIC_ROOT, 'admin')
            if os.path.exists(admin_path):
                self.stdout.write(self.style.SUCCESS("✅ Admin static files found"))
                admin_contents = os.listdir(admin_path)
                self.stdout.write(f"Admin static files: {admin_contents}")
            else:
                self.stdout.write(self.style.ERROR("❌ Admin static files NOT found"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ STATIC_ROOT does not exist: {settings.STATIC_ROOT}"))
        
        # Try to find admin CSS using Django's finders
        admin_css = finders.find('admin/css/base.css')
        if admin_css:
            self.stdout.write(self.style.SUCCESS(f"✅ Found admin CSS at: {admin_css}"))
        else:
            self.stdout.write(self.style.ERROR("❌ Could not find admin CSS"))
        
        self.stdout.write(self.style.SUCCESS('\nStatic files check complete!'))
