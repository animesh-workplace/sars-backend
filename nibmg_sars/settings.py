import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.getenv('DEBUG'))

ALLOWED_HOSTS = ['*']

# Application definition
DEFAULT_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
	'corsheaders',
	'django_extensions',
	'rest_framework',
	'rest_framework_swagger',
	'rest_framework.authtoken',
	'django_celery_beat',
	'django_celery_results',
	'celery_progress',
	'channels',
]

LOCAL_APPS = [
	'accounts',
	'sequences',
]

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nibmg_sars.urls'

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
            ],
        },
    },
]

ASGI_APPLICATION = 'nibmg_sars.asgi.application'

# Channel Layers
CHANNEL_LAYERS = {
	"default": {
		"BACKEND": "channels_redis.core.RedisChannelLayer",
		"CONFIG": {
			"hosts": [(os.getenv('CELERY_BROKER_NAME'), os.getenv('CELERY_BROKER_PORT'))],
		},
	},
}

# Database
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': BASE_DIR / 'media' / 'database' / 'db.sqlite3',
	}
}

# Password validation
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
LANGUAGE_CODE   = os.getenv('LANGUAGE_CODE')
TIME_ZONE       = os.getenv('TIME_ZONE')
USE_I18N        = os.getenv('USE_I18N')
USE_L10N        = os.getenv('USE_L10N')
USE_TZ          = os.getenv('USE_TZ')

# Static files (CSS, JavaScript, Images)
STATIC_ROOT     = os.path.join(BASE_DIR, 'static')
STATIC_URL      = f"/{os.getenv('BASE_URL')}static/"

# Media files (CSS, JavaScript, Images)
MEDIA_ROOT      = os.path.join(BASE_DIR, 'media')
MEDIA_URL       = f"/{os.getenv('BASE_URL')}media/"

#Test Zone
REMOTE_ROOT     = os.getenv('REMOTE_ROOT')
HOST_ROOT       = os.path.join(BASE_DIR, 'media')

# Authentication user model
AUTH_USER_MODEL = 'accounts.Accounts'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cross Origin Resource Sharing
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
# CORS_ORIGIN_WHITELIST = [
#     'http://localhost:3030',
# ]
# CORS_ORIGIN_REGEX_WHITELIST = [
#     'http://localhost:3030',
# ]

# Celery Settings
CELERY_BROKER_URL           = f"redis://{ os.getenv('CELERY_BROKER_NAME') }:{ os.getenv('CELERY_BROKER_PORT') }"
CELERY_RESULT_BACKEND       = os.getenv('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT       = ['application/json']
CELERY_TASK_SERIALIZER      = 'json'
CELERY_RESULT_SERIALIZER    = 'json'
CELERY_TIMEZONE             = TIME_ZONE

# REST API Settings
from nibmg_sars.rest_configuration.main import *
