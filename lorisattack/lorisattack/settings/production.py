from .base import *

# zappa deploy url prefix
# -- Maps to zappa_settings.json deployed stage name
URL_PREFIX = '/dev'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = f'{URL_PREFIX}/admin/'

# double-check, this is hard coded domain restriction. (Also filtered on User creation Login
SOCIAL_AUTH_GOOGLE_OAUTH2_DOMAINS_RAW = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_DOMAIN', None)
if SOCIAL_AUTH_GOOGLE_OAUTH2_DOMAINS_RAW:
    SOCIAL_AUTH_GOOGLE_OAUTH2_DOMAINS = [i.strip() for i in SOCIAL_AUTH_GOOGLE_OAUTH2_DOMAINS_RAW.split(',')]
    SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = SOCIAL_AUTH_GOOGLE_OAUTH2_DOMAINS  # TODO: Confirm that this works...

ALLOWED_HOSTS.append(os.getenv('ALLOWED_HOST', '*'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'callippus'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': 3306,
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
    }
}

DISPLAY_ADMIN_AUTH_FOR_MODELBACKEND = False
