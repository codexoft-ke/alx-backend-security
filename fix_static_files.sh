#!/bin/bash
# Static files fix script for PythonAnywhere

echo "Fixing static files for Django admin dashboard..."

# Activate virtual environment
source venv/bin/activate

# Create static directories
mkdir -p static
mkdir -p staticfiles
mkdir -p media

# Collect static files with the production settings
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=backend_security.production_settings

# Set proper permissions
chmod -R 755 static/
chmod -R 755 staticfiles/

echo "Static files collected successfully!"
echo ""
echo "Files collected in:"
ls -la static/
echo ""
echo "Next steps for PythonAnywhere:"
echo "1. Go to your Web tab in PythonAnywhere dashboard"
echo "2. Scroll down to 'Static files' section"
echo "3. Add the following mapping:"
echo "   URL: /static/"
echo "   Directory: /home/codexoft/alx-backend-security/static/"
echo "4. Click 'Reload' button"
echo "5. Test admin dashboard: https://codexoft.pythonanywhere.com/admin/"
echo ""
echo "The Django admin should now have proper CSS and JS styling!"
