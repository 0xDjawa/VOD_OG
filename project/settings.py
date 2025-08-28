"""
Django settings for project project.

Generated# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'video',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

CORS_ALLOWED_ORIGINS = [
    "http://202.169.232.239:8047",
]-admin startproject' using Django 5.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os
from pathlib import Path
import django

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# File Upload Settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440000  # 2.5GB in bytes
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440000  # 2.5GB in bytes
FILE_UPLOAD_TEMP_DIR = '/tmp/django_uploads'  # Temporary directory for file uploads
FILE_UPLOAD_PERMISSIONS = 0o644  # File permissions
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755  # Directory permissions
FILE_UPLOAD_TIMEOUT = 7200  # 2 hours timeout

# Media files configuration
MEDIA_ROOT = '/var/www/html/media'  # Apache/Nginx web folder
MEDIA_URL = '/media/'  # URL prefix for media files
WEB_MEDIA_URL = 'http://202.169.232.239:8047/media/'  # Full URL for accessing media

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-ioj%e(3yul-ix!(zj-7a#gemy=#j(7ko@f&2v%+g!fp8=$dbk+'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/html/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

ALLOWED_HOSTS = ['202.169.232.239', 'localhost', '127.0.0.1']

# File Upload Settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 2621440000  # 2.5GB in bytes
FILE_UPLOAD_MAX_MEMORY_SIZE = 2621440000  # 2.5GB in bytes
FILE_UPLOAD_TEMP_DIR = '/tmp/django_uploads'  # Temporary directory for file uploads
FILE_UPLOAD_PERMISSIONS = 0o644  # File permissions
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755  # Directory permissions

# Increase timeout for large file uploads (in seconds)
FILE_UPLOAD_TIMEOUT = 7200  # 2 hours

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'video'
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

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/html/static'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/html/media'  # Local media directory for processed videos


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# Added by me
django.setup()
django.setup()
