"""
Production settings for PythonAnywhere deployment
"""
from .settings import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Update this with your PythonAnywhere domain
ALLOWED_HOSTS = ['codexoft.pythonanywhere.com', 'www.codexoft.pythonanywhere.com']

# Database for production (you can use MySQL on PythonAnywhere)
# Uncomment and configure if using MySQL:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'codexoft$alx_security',
#         'USER': 'codexoft',
#         'PASSWORD': 'your_mysql_password',
#         'HOST': 'codexoft.mysql.pythonanywhere-services.com',
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#         },
#     }
# }

# For SQLite in production (simpler setup)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'production_db.sqlite3',
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Additional static files directories
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles'),
]

# Static files finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Your Redis Cloud configuration (already configured)
# CELERY_BROKER_URL and CACHES are already set correctly

# Override cache configuration for production
# Use a fallback cache configuration that's more reliable
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake-prod',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# If you want to use Redis cache (optional, comment out above and uncomment below)
# Make sure django-redis is installed: pip install django-redis
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://default:wzBmvpySKe81affRnILnY0DWitpbVrRu@redis-12795.c57.us-east-1-4.ec2.redns.redis-cloud.com:12795/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#             'CONNECTION_POOL_KWARGS': {
#                 'retry_on_timeout': True,
#                 'socket_timeout': 5,
#                 'socket_connect_timeout': 5,
#             }
#         },
#         'TIMEOUT': 300,
#     }
# }

# Logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'ip_tracking.log'),
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'ip_tracking': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
