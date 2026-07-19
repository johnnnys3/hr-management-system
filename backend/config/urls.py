from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('health.urls')),
    path('api/', include('audit.urls')),
    path('api/', include('accounts.urls')),
    path('api/', include('iam.urls')),
    path('api/', include('departments.urls')),
    path('api/', include('employees.urls')),
    path('api/', include('reporting_structure.urls')),
    path('api/', include('recruitment.urls')),
    path('api/', include('onboarding.urls')),
    path('api/', include('notifications.urls')),
    path('api/', include('leave.urls')),
    path('api/', include('dashboard.urls')),
    path('api/', include('compensation.urls')),
]
