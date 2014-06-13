# Settings for role development

# Import generic settings
from common import *

# Add or override settings

DEBUG = False
TEMPLATE_DEBUG = DEBUG
SEND_BROKEN_LINK_EMAILS = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mikael_och_maria_se_production',
        'HOST': '',
        'PORT': '3306',
        'USER': 'production',
        'PASSWORD': 'production'
    }
}

STATIC_ROOT = "/home/webapp/public_static/static/"

STATIC_URL = '/static/'

# AWS access keys for mikaelochmaria_se with access to SES
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""

ROLE_NAME = "Production"

