"""
WSGI config for PythonAnywhere deployment.
"""

import os
import sys

# Add your project directory to the sys.path
path = '/home/codexoft/alx-backend-security'  # Replace 'yourusername' with your actual username
if path not in sys.path:
    sys.path.insert(0, path)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_security.production_settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
