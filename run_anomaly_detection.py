#!/usr/bin/env python
"""
Scheduled task script for PythonAnywhere
Run this as a scheduled task every hour
"""
import os
import sys
import django

# Add project to path
sys.path.insert(0, '/home/codexoft/alx-backend-security')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_security.production_settings')
django.setup()

# Run the anomaly detection
from ip_tracking.tasks import detect_anomalies

if __name__ == '__main__':
    print("Running anomaly detection...")
    result = detect_anomalies()
    print(f"Anomaly detection completed: {result}")
