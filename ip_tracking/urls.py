from django.urls import path
from . import views

app_name = 'ip_tracking'

urlpatterns = [
    path('test/', views.test_view, name='test'),
    path('login/', views.sensitive_login_view, name='login'),
    path('api/authenticated/', views.authenticated_api_view, name='authenticated_api'),
    path('admin/sensitive/', views.admin_sensitive_view, name='admin_sensitive'),
    path('stats/', views.ip_stats_view, name='ip_stats'),
]
