#!/bin/bash
# Fix deployment script for PythonAnywhere

echo "Applying fixes for Redis cache configuration..."

# Activate virtual environment
source venv/bin/activate

# Pull latest changes (if using git)
# git pull origin main

# Collect static files
python manage.py collectstatic --noinput --settings=backend_security.production_settings

# Run any pending migrations
python manage.py migrate --settings=backend_security.production_settings

echo "Fixes applied successfully!"
echo ""
echo "Next steps:"
echo "1. Go to your PythonAnywhere Web tab"
echo "2. Click 'Reload' to restart your web app"
echo "3. Test the application at your domain"
echo ""
echo "The cache configuration has been fixed to use local memory cache"
echo "which is more reliable on PythonAnywhere free accounts."
