from .base import *


DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'circleci_test',
        'USER': 'root',
        'PASSWORD': 'mysecretpassword',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# zappa deploy url prefix
# -- Maps to zappa_settings.json deployed stage name
URL_PREFIX = ''


BOTO3_ENDPOINTS = {
    's3': 'http://localhost:4572',  # localstack endpoint
}

# default domain
DEFAULT_ROOT_URL = f'http://localhost:8000'
ROOT_URL = os.getenv('ROOT_URL', DEFAULT_ROOT_URL)