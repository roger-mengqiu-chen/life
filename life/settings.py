import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

SECRET_KEY = 'django-insecure-xw&5k*a5_$@ue-e*@n%(4-313r*7-u)ur#p!3x80hnmx01jngt'

EXCHANGE_RATE_API_KEY = os.getenv('EXCHANGE_RATE_API_KEY', '')

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'rest_framework',
    'rangefilter',
    'mylife',
    'investment_journal',
    'django_plotly_dash'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_plotly_dash.middleware.ExternalRedirectionMiddleware',
    'django_plotly_dash.middleware.BaseMiddleware',
]
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django_plotly_dash.finders.DashComponentFinder'
]

PLOTLY_DASH = {
    "serve_locally": True,  # Ensures it looks for the local plotly.min.js
}


ROOT_URLCONF = 'life.urls'

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

WSGI_APPLICATION = 'life.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Edmonton'

USE_I18N = True

USE_TZ = True

X_FRAME_OPTIONS = 'SAMEORIGIN'

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MERCHANTS = {
    'amazon', 'costco', 'esso', 'steam games', 'home depot', 'sport chek',
    'shoe warehouse', 'decathlon', 'mazda', 'polo factory store',
    'longview jerky shop', 'minutekeyvending', 'alberta parks', 'mouser electronics',
    'petsmart', 'T&T', 'ROGERS', 'purebread yvr', 'wow chicken', 'triple o\'s',
    'tokyo street market', 'jollibee', 'koodo mobile', 'enmax energy', 'telus comm',
    'NIUBEST HAND-PULLED NOODL', 'A&W', 'EFT CREDIT TPS/GST', 'PROPERTY TAXES', 'PERSONAL LOANS',
    'PAYROLL DEPOSIT', 'REMISE CARBONE/CARBON REBATE', 'OREILLY', 'LYFT', 'ATM DEPOSIT', 'PIZZA 64',
    'TST-Kama', 'AMZN', 'COURSERA', 'GOOGLE', 'FIDO Mobile', 'DOLLARAMA',
}

TRANSACTION_TIME_FORMAT = ('%Y-%m-%d', '%B %d, %Y')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname:<8} | {name:<20} | {module}:{lineno} - {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'info.log'),
            'formatter': 'verbose',
            'maxBytes': 1048576,
            'backupCount': 5,
            'level': 'DEBUG',
        }
    },
    'loggers': {
        'django.server': {
            'handlers': ['console', 'file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'life': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}
