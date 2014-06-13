# Settings for role development

# Import generic settings
from common import *

# Add or override settings

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mikael_och_maria_se_development',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'USER': 'development',
        'PASSWORD': 'development'
    }
}

STATIC_ROOT = "/home/webapp/public_static/static/"

STATIC_URL = '/static/'

# AWS access keys for mikaelochmaria_se with access to SES
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""

ROLE_NAME = "Development"