"""
Django settings for the Core Project.
Final Version: Database + Cloudinary + Fix for Missing Styles
"""

import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
import dj_database_url

# --- BASE CONFIGURATION ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SECURITY ---
SECRET_KEY = os.environ.get('SECRET_KEY', "django-insecure-local-key")
DEBUG = 'RENDER' not in os.environ
ALLOWED_HOSTS = ['*']

INTERNAL_IPS = ["127.0.0.1"]

# --- APPS ---
INSTALLED_APPS = [
    'jazzmin',
    'tailwind',
    'theme',
    'django_browser_reload',
    'widget_tweaks',

    # Cloudinary (Must be before django.contrib.staticfiles)
    'cloudinary_storage',
    'cloudinary',

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.humanize',

    'users.apps.UsersConfig',
    'marketplace.apps.MarketplaceConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise must be directly after SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# --- DATABASE ---
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600
    )
}

# --- AUTHENTICATION ---
AUTH_USER_MODEL = 'users.CustomUser'
AUTH_PASSWORD_VALIDATORS = []

# --- LANGUAGES ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [
    ('en', _('English')),
    ('am', _('Amharic')),
    ('om', _('Afaan Oromoo')),
    ('so', _('Somali')),
    ('ti', _('Tigrinya')),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

# --- STATIC FILES (CSS/JS) ---
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# *** FIX APPLIED HERE ***
# We switched to CompressedStaticFilesStorage.
# The 'Manifest' version fails if any file is missing, causing your "0 files copied" error.
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Only add the static directory if it actually exists to prevent errors
STATICFILES_DIRS = []
if (BASE_DIR / 'static').exists():
    STATICFILES_DIRS = [BASE_DIR / 'static']

# --- MEDIA FILES (IMAGES - CLOUDINARY) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# If on Server: Use Cloudinary for images
if 'RENDER' in os.environ:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    # If Local: Use computer folder
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Cloudinary Configuration (Read from Environment)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# --- TAILWIND ---
TAILWIND_APP_NAME = 'theme'
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if 'RENDER' in os.environ:
    NPM_BIN_PATH = 'npm'
else:
    # Adjust this path if your local windows path is different
    NPM_BIN_PATH = r"C:/Program Files/nodejs/npm.cmd"

# --- TELEBIRR ---
TELEBIRR_APP_ID = 'your-app-id'
TELEBIRR_APP_KEY = 'your-app-key'
TELEBIRR_PUBLIC_KEY = 'your-public-key'
TELEBIRR_NOTIFY_URL = 'http://127.0.0.1:8000/telebirr/notify/'
TELEBIRR_RETURN_URL = 'http://127.0.0.1:8000/telebirr/success/'

# --- JAZZMIN ---
JAZZMIN_SETTINGS = {
    "site_title": "Arbor Marketplace Control",
    "site_header": "Arbor Market",
    "site_brand": "A",
    "theme": "cosmo",
    "dark_mode_theme": "darkly",
    "default_icon_parents": "fas fa-leaf",
    "default_icon_children": "fas fa-shopping-cart",
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "marketplace": "fas fa-store",
        "marketplace.product": "fas fa-tag",
        "marketplace.order": "fas fa-truck",
    },
    "navbar_small_text": False,
    "sidebar_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_flat_style": True,
    "button_classes": {
        "primary": "btn-primary",
        "success": "btn-success",
        "danger": "btn-danger",
    },
    "disable_user_sidebar": False,
}

JAZZMIN_UI_TWEAKS = {
    "show_ui_builder": False,
    "header_fixed": True,
    "footer_fixed": False,
    "sidebar_fixed": True,
}