"""
Django settings for the Core Project.
Final Version: Django 5 Compatible (Fixes Image Storage)
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
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # Must be before cloudinary_storage in some setups, but usually after is fine.
    'django.contrib.humanize',

    # Third Party
    'tailwind',
    'theme',
    'django_browser_reload',
    'widget_tweaks',

    # CLOUDINARY (Images)
    'cloudinary_storage',
    'cloudinary',

    # Local Apps
    'users.apps.UsersConfig',
    'marketplace.apps.MarketplaceConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Images/CSS caching
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
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

# --- STATIC FILES (CSS) ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# --- MEDIA FILES (IMAGES) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- DJANGO 5 STORAGES CONFIGURATION (THE FIX) ---
# We configure both Static (CSS) and Media (Images) here.
STORAGES = {
    "default": {
        # By default, use local storage (good for development)
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # Use Whitenoise for CSS (Compressed)
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# IF WE ARE ON RENDER -> SWITCH TO CLOUDINARY
if 'RENDER' in os.environ:
    STORAGES["default"]["BACKEND"] = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Cloudinary Credentials (Must match Render Environment Variables)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# --- TAILWIND ---
TAILWIND_APP_NAME = 'theme'
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
NPM_BIN_PATH = 'npm' if 'RENDER' in os.environ else r"C:/Program Files/nodejs/npm.cmd"

# --- JAZZMIN ---
JAZZMIN_SETTINGS = {
    "site_title": "Arbor Marketplace Control",
    "site_header": "Arbor Market",
    "site_brand": "A",
    "theme": "cosmo",
    "dark_mode_theme": "darkly",
    "default_icon_parents": "fas fa-leaf",
    "default_icon_children": "fas fa-shopping-cart",
    "navbar_small_text": False,
    "sidebar_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_flat_style": True,
    "disable_user_sidebar": False,
}
JAZZMIN_UI_TWEAKS = {
    "show_ui_builder": False,
    "header_fixed": True,
    "footer_fixed": False,
    "sidebar_fixed": True,
}