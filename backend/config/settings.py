"""
Django settings for the HRMS backend.

Configuration is environment-driven per ADR-0009 (containerised deployment,
hosting target deferred): every setting that varies between local, on-premises,
and cloud deployment is read from the environment rather than hard-coded, so
resolving TBD-003 changes configuration, not this file.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in ('1', 'true', 'yes', 'on')


SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DEBUG = env_bool('DJANGO_DEBUG', False)

ALLOWED_HOSTS = [h for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if h]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'health.apps.HealthConfig',
    'audit.apps.AuditConfig',
    'mail.apps.MailConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# ADR-0003: PostgreSQL for all HRMS data.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ['POSTGRES_DB'],
        'USER': os.environ['POSTGRES_USER'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files
# Caddy serves the built React SPA directly; Django's STATIC_URL covers only
# Django's own static assets (admin, DRF browsable API), collected here.

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Session-cookie authentication (ADR-0004)
# HttpOnly, Secure, SameSite=Lax; single-origin deployment (ADR-0009) is what
# makes this workable without SameSite=None.

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


# Celery (ADR-0006)
# Two Redis instances: broker (noeviction, AOF) and cache (allkeys-lru).
# Never point both at the same instance — that reintroduces the eviction
# path ADR-0006 exists to close.

CELERY_BROKER_URL = os.environ['CELERY_BROKER_URL']
CELERY_TASK_IGNORE_RESULT = True
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ['REDIS_CACHE_URL'],
    }
}


# Mail dispatch (ADR-0011)
# Django's SMTP backend against env-driven settings; no provider is pinned
# (SES, SendGrid, ...), matching the deferred-hosting posture ADR-0009 and
# ADR-0007 already take — a provider choice is a configuration change, not
# a code change. EMAIL_BACKEND defaults to the console backend so tests and
# an unconfigured environment don't attempt a real SMTP connection.

EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '25'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', False)
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '10'))
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'hrms@localhost')


# Delivery-failure logging (ADR-0011): application logs, never audit_log —
# HRMS-NFR-022 fixes audit_log's five categories and delivery failure is in
# none of them.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'mail': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# Object storage (ADR-0007)
# MinIO in self-hosted deployment, via the S3-compatible API through
# django-storages. Bucket is private; the application issues short-lived
# signed URLs rather than serving objects directly (application-code concern
# for a later module, not this one).

STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'access_key': os.environ['MINIO_ACCESS_KEY'],
            'secret_key': os.environ['MINIO_SECRET_KEY'],
            'bucket_name': os.environ['MINIO_BUCKET_NAME'],
            'endpoint_url': os.environ['MINIO_ENDPOINT_URL'],
            'default_acl': 'private',
            'querystring_auth': True,
        },
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}
