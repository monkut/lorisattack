"""
Django settings for callippus project.

Generated by 'django-admin startproject' using Django 2.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
import os
from pathlib import PurePath
from django.utils.translation import ugettext_lazy as _
from django.conf.locale.en import formats as en_formats
from django.conf.locale.ja import formats as ja_formats


ja_formats.DATETIME_FORMAT = 'c'
en_formats.DATETIME_FORMAT = 'c'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = PurePath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%$no7h*v7^7z)azux$6tsdf2*m2%tgxj!z&5vl%(a&v6-(o%d#+!2&'

S3_BUCKET_SUFFIX = '19d91jp'  # to make buckets unique

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'social_django',
    'storages',  # Configuration for storing static/media files on S3
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'commons',
    'accounts',
    'staticsites',
    'news',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'lorisattack.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'callippus.context_processors.global_view_additional_context',  # PROVIDES settings.URL_PREFIX to context
            ],
        },
    },
]

WSGI_APPLICATION = 'lorisattack.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
LANGUAGES = [
    ('ja', _('Japanese')),
    ('en', _('English')),
]

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = 'ja'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DISPLAY_ADMIN_AUTH_FOR_MODELBACKEND = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

SITE_HEADER = 'Organizational StaticSite CMS (callippus)'
SITE_TITLE = SITE_HEADER

# Authentication
# http://docs.djangoproject.com/en/dev/ref/settings/?from=olddocs#authentication-backends
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)
URL_PREFIX = ''  # needed to support a prefix on urls (for zappa deployment)

SOCIAL_AUTH_POSTGRES_JSONFIELD = False
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_OAUTH2_KEY', None)  # client ID
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_OAUTH2_SECRET', None)

# for integration of social_auth with admin
# https://python-social-auth.readthedocs.io/en/latest/configuration/django.html
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']

# for identification of SOCIAL_AUTH_USER
# http://python-social-auth.readthedocs.io/en/latest/configuration/settings.html#user-model
SOCIAL_AUTH_USER_MODEL = 'accounts.OrganizationUser'
AUTH_USER_MODEL = SOCIAL_AUTH_USER_MODEL
SOCIAL_AUTH_LOGIN_REDIRECT_URL = f'{URL_PREFIX}/admin/'

DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', 'INFO')
DJANGO_CORE_LOG_LEVEL = os.getenv('DJANGO_CORE_LOG_LEVEL', 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '{asctime} [{levelname:5}] ({name}) {funcName}: {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': DJANGO_CORE_LOG_LEVEL,  # Change to DEBUG to see db queries
        },
        'accounts': {
            'handlers': ['console'],
            'level': DJANGO_LOG_LEVEL,
            'propagate': True,
        },
        'staticsites': {
            'handlers': ['console'],
            'level': DJANGO_LOG_LEVEL,
            'propagate': True,
        }
    },
}

DEFAULT_REGION = 'ap-northeast-1'
AWS_REGION = os.getenv('AWS_DEFAULT_REGION', DEFAULT_REGION)

DEFAULT_AWS_S3_DOMAIN = f's3.{AWS_REGION}.amazonaws.com'
AWS_S3_DOMAIN = os.getenv('AWS_S3_DOMAIN', DEFAULT_AWS_S3_DOMAIN)
DEFAULT_S3_ENDPOINT_URL = f'https://{AWS_S3_DOMAIN}'
BOTO3_ENDPOINTS = {
    's3': os.getenv('S3_ENDPOINT_URL', DEFAULT_S3_ENDPOINT_URL),
}

# update django-storages endpoint
AWS_S3_ENDPOINT_URL = BOTO3_ENDPOINTS['s3']

# refer to:
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATIC_ROOT = '/static/'

# S3 Bucket Config
# -- for static files
#    (For django-storages)
# --> Bucket Created in infrastructure/README.md procedure
DEFAULT_AWS_STORAGE_BUCKET_NAME = f'lorisattack-staticfiles-dev-{S3_BUCKET_SUFFIX}'

AWS_DEFAULT_ACL = None  # to silence warning
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', DEFAULT_AWS_STORAGE_BUCKET_NAME)  # django-storages required setting
S3_STATICFILES_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_DOMAIN}'
AWS_S3_CUSTOM_DOMAIN = S3_STATICFILES_DOMAIN  # django-storages required setting
schema = 'https://' if AWS_S3_DOMAIN == DEFAULT_AWS_S3_DOMAIN else 'http://'  # set http if using local dev
STATIC_URL = f'{schema}{S3_STATICFILES_DOMAIN}/'

MAX_INDEX_NEWSITEMS = int(os.getenv('MAX_INDEX_NEWSITEMS', '6'))
DEFAULT_NEWS_ITEMS_PER_PAGE = '5'
NEWS_ITEMS_PER_PAGE = int(os.getenv('NEWS_ITEMS_PER_PAGE', DEFAULT_NEWS_ITEMS_PER_PAGE))
