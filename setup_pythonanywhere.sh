#!/bin/bash
# Setup script for PythonAnywhere deployment

echo "Setting up ALX Backend Security on PythonAnywhere..."

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Collect static files
python manage.py collectstatic --noinput --settings=backend_security.production_settings

# Run migrations
python manage.py migrate --settings=backend_security.production_settings

# Create superuser (you'll need to run this manually)
echo "To create a superuser, run:"
echo "python manage.py createsuperuser --settings=backend_security.production_settings"

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update ALLOWED_HOSTS in production_settings.py with your domain"
echo "2. Configure Web App in PythonAnywhere dashboard"
echo "3. Set up task scheduling for Celery tasks"
