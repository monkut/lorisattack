from .base import *


DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lorisattack',
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