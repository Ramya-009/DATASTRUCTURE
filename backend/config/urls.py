from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # REST APIs
    path('api/auth/', include('users.urls')),
    path('api/tanks/', include('tanks.urls')),
    path('api/water/', include('water.urls')),
    path('api/distribution/', include('distribution.urls')),
    path('api/leakage/', include('leakage.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/reports/', include('reports.urls')),

    # Frontend Navigation Routes
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),

    # User Portal Pages
    path('user/dashboard/', TemplateView.as_view(template_name='user/dashboard.html'), name='user-dashboard'),
    path('user/request-water/', TemplateView.as_view(template_name='user/request-water.html'), name='user-request-water'),
    path('user/usage/', TemplateView.as_view(template_name='user/usage.html'), name='user-usage'),
    path('user/schedule/', TemplateView.as_view(template_name='user/schedule.html'), name='user-schedule'),
    path('user/leakage/', TemplateView.as_view(template_name='user/leakage.html'), name='user-leakage'),
    path('user/notifications/', TemplateView.as_view(template_name='user/notifications.html'), name='user-notifications'),

    # Admin Portal Pages
    path('admin/dashboard/', TemplateView.as_view(template_name='admin/dashboard.html'), name='admin-dashboard'),
    path('admin/users/', TemplateView.as_view(template_name='admin/users.html'), name='admin-users'),
    path('admin/areas/', TemplateView.as_view(template_name='admin/areas.html'), name='admin-areas'),
    path('admin/tanks/', TemplateView.as_view(template_name='admin/tanks.html'), name='admin-tanks'),
    path('admin/requests/', TemplateView.as_view(template_name='admin/requests.html'), name='admin-requests'),
    path('admin/distribution/', TemplateView.as_view(template_name='admin/distribution.html'), name='admin-distribution'),
    path('admin/leakage/', TemplateView.as_view(template_name='admin/leakage.html'), name='admin-leakage'),
    path('admin/reports/', TemplateView.as_view(template_name='admin/reports.html'), name='admin-reports'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
