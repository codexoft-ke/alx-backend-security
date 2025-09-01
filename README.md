# ALX Backend Security - IP Tracking System

A comprehensive Django-based IP tracking and security system that provides logging, blacklisting, geolocation, rate limiting, and anomaly detection capabilities.

## 🚀 Features

### Task 0: Basic IP Logging Middleware ✅
- **IP Address Tracking**: Logs every incoming request with IP, timestamp, and path
- **Middleware Integration**: Seamlessly integrated into Django's middleware stack
- **Database Storage**: Persistent storage of request logs with the `RequestLog` model

### Task 1: IP Blacklisting ✅
- **Dynamic IP Blocking**: Block malicious IPs with HTTP 403 responses
- **Management Commands**: Easy-to-use command-line tools for blocking/unblocking IPs
- **Admin Interface**: Web-based administration for managing blocked IPs
- **Caching**: Efficient Redis-based caching for fast IP lookup

### Task 2: IP Geolocation Analytics ✅
- **Geographic Data**: Automatically fetch country, city, and region information
- **Multiple API Support**: Fallback support for multiple geolocation services
- **24-hour Caching**: Efficient caching to reduce API calls and improve performance
- **Enhanced Logging**: Location-aware request logging

### Task 3: Rate Limiting by IP ✅
- **Tiered Rate Limits**: Different limits for authenticated vs anonymous users
- **Sensitive Endpoint Protection**: Special protection for login and admin endpoints
- **Django-ratelimit Integration**: Production-ready rate limiting with Redis backend
- **Configurable Limits**: Easy to adjust rate limits per endpoint

### Task 4: Anomaly Detection ✅
- **Automated Detection**: Hourly Celery tasks to identify suspicious behavior
- **Multiple Detection Methods**: 
  - High volume requests (>100 requests/hour)
  - Sensitive path access patterns
  - Rapid-fire request detection
  - Geographic anomalies
- **Severity Classification**: Low, medium, high, and critical threat levels
- **Auto-blocking**: Automatic blocking of critical threats

## 📁 Project Structure

```
alx-backend-security/
├── backend_security/          # Django project settings
│   ├── __init__.py
│   ├── settings.py           # Main configuration
│   ├── urls.py              # URL routing
│   ├── wsgi.py              # WSGI configuration
│   ├── asgi.py              # ASGI configuration
│   └── celery.py            # Celery configuration
├── ip_tracking/              # Main IP tracking application
│   ├── __init__.py
│   ├── admin.py             # Django admin configuration
│   ├── apps.py              # App configuration
│   ├── middleware.py        # IP tracking and blocking middleware
│   ├── models.py            # Database models
│   ├── views.py             # API endpoints
│   ├── urls.py              # URL patterns
│   ├── geolocation.py       # IP geolocation service
│   ├── tasks.py             # Celery background tasks
│   ├── management/          # Django management commands
│   │   └── commands/
│   │       └── block_ip.py  # IP blocking command
│   └── migrations/          # Database migrations
├── manage.py                # Django management script
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Django 5.2+
- Redis (for caching and Celery)
- PostgreSQL/MySQL (for production) or SQLite (for development)

### 1. Clone the Repository
```bash
git clone https://github.com/codexoft-ke/alx-backend-security.git
cd alx-backend-security
```

### 2. Install Dependencies
```bash
pip install django celery redis requests django-ratelimit
```

### 3. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Start Redis Server
```bash
redis-server
```

### 6. Start Celery Worker (in separate terminal)
```bash
celery -A backend_security worker -l info
```

### 7. Start Celery Beat (in separate terminal)
```bash
celery -A backend_security beat -l info
```

### 8. Run Development Server
```bash
python manage.py runserver
```

## 🔧 Configuration

### Middleware Setup
The IP tracking middleware is already configured in `settings.py`:
```python
MIDDLEWARE = [
    # ... other middleware
    'ip_tracking.middleware.IPTrackingMiddleware',
]
```

### Rate Limiting Configuration
Rate limits are configured per view:
- Anonymous users: 5 requests/minute on sensitive endpoints
- Authenticated users: 10 requests/minute on API endpoints
- Admin endpoints: 3 requests/minute

### Geolocation APIs
The system uses multiple geolocation providers with automatic fallback:
1. ipapi.co (primary)
2. ip-api.com (fallback)

## 📚 Usage

### Blocking IPs via Command Line
```bash
# Block a single IP
python manage.py block_ip 192.168.1.100 --reason "Malicious activity"

# Block a network range
python manage.py block_ip 192.168.1.0/24 --reason "Suspicious network"

# Unblock an IP
python manage.py block_ip 192.168.1.100 --unblock

# List all blocked IPs
python manage.py block_ip --list
```

### API Endpoints
- `GET /ip-tracking/test/` - Test endpoint to verify middleware
- `POST /ip-tracking/login/` - Rate-limited login endpoint
- `GET /ip-tracking/api/authenticated/` - Authenticated API endpoint
- `GET /ip-tracking/admin/sensitive/` - Highly rate-limited admin endpoint
- `GET /ip-tracking/stats/` - IP statistics for current user

### Admin Interface
Access the Django admin at `/admin/` to:
- View request logs with geolocation data
- Manage blocked IPs
- Review suspicious IP flags
- Bulk operations on suspicious IPs

## 🔍 Monitoring & Analytics

### Request Logs
All requests are logged with:
- IP address
- Timestamp
- Request path
- Geographic location (country, city, region)
- Coordinates (latitude, longitude)

### Suspicious Activity Detection
The system automatically detects:
- **High Volume**: >100 requests/hour from single IP
- **Sensitive Access**: Multiple attempts to access admin/login endpoints
- **Rapid Fire**: >20 requests in 5-minute windows
- **Geographic Anomalies**: Requests from multiple countries

### Security Reports
Daily security reports include:
- Total requests and unique IPs
- Currently blocked IPs
- Suspicious activity flags
- Top countries by request volume

## 🚨 Security Considerations

### Privacy Compliance
- IP addresses can be anonymized for GDPR compliance
- Configurable data retention periods
- Geographic data is cached to minimize API calls

### Performance Optimization
- Redis caching for blocked IP lookups
- Geolocation data caching (24 hours)
- Efficient database queries with proper indexing

### Rate Limiting Best Practices
- Different limits for different user types
- Graceful degradation with informative error messages
- Bypass options for trusted IP ranges

## 🧪 Testing

Run the test suite to verify functionality:
```bash
python manage.py test ip_tracking
```

## 📈 Monitoring

### Log Files
- Application logs: `ip_tracking.log`
- Celery logs: Configure in your deployment

### Metrics to Monitor
- Request volume by IP
- Blocked request attempts
- Geolocation API usage
- Anomaly detection accuracy

## 🚀 Production Deployment

### Environment Variables
```bash
export DJANGO_SETTINGS_MODULE=backend_security.settings
export CELERY_BROKER_URL=redis://localhost:6379/0
export DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### Required Services
1. **Web Server**: Gunicorn + Nginx
2. **Database**: PostgreSQL/MySQL
3. **Cache**: Redis
4. **Queue**: Celery with Redis broker
5. **Scheduler**: Celery Beat

### Scaling Considerations
- Use multiple Celery workers for high-volume sites
- Consider rate limiting at the load balancer level
- Implement log rotation for large-scale deployments

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Review the documentation
- Check the logs for error details

## 🔄 Changelog

### v1.0.0
- ✅ Basic IP logging middleware
- ✅ IP blacklisting system
- ✅ Geolocation analytics
- ✅ Rate limiting implementation
- ✅ Anomaly detection with Celery
- ✅ Admin interface
- ✅ Management commands
- ✅ Comprehensive testing