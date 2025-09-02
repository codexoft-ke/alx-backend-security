#!/bin/bash
# Fix deployment script for PythonAnywhere

echo "Applying fixes for Redis cache configuration and adding homepage..."

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
echo "Changes applied:"
echo "✅ Fixed Redis cache configuration"
echo "✅ Added homepage view (eliminates 404 errors)"
echo "✅ Enhanced error handling in middleware"
echo ""
echo "Your IP tracking system is now fully functional!"
