"""
Django settings for test_project project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q2c&y%go(h!+ipyhpg+%ld$td5m^s&30ks-v5l3%_rxl1(6v%f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

DEFAULT_DJANGO_INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

]

LUZFCB_DJDOCUMENTS_APPS = [
    # dependencies
    'luzfcb_dj_simplelock.apps.DjSimpleLockAppConfig',
    'simple_history',
    'spurl',
    'braces',
    'crispy_forms',
    'captcha',
    'dal',
    'dal_select2',
    # end dependencies

    # development dependencies
    'debug_toolbar',
    # end development dependencies

    'luzfcb_djdocuments',
    'test_app'
]

INSTALLED_APPS = DEFAULT_DJANGO_INSTALLED_APPS + LUZFCB_DJDOCUMENTS_APPS

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'test_project.urls'

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

WSGI_APPLICATION = 'test_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
USE_PG = True

if USE_PG:
    DB_ENGINE_CONFIG = {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        'NAME': 'luzfcb_djdocuments_testdb',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
    }
else:
    DB_ENGINE_CONFIG = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }

DATABASES = {
    'default': DB_ENGINE_CONFIG
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

FONT_DIR = os.path.join(
    os.path.dirname(BASE_DIR), 'tests', 'test_project', 'contrib', 'fonts')

# django-simple-captcha config
CAPTCHA_FONT_PATH = (
    os.path.join(FONT_DIR, 'HomemadeApple.ttf'),
    os.path.join(FONT_DIR, 'RockSalt.ttf'),
    os.path.join(FONT_DIR, 'ShadowsIntoLight.ttf'),
)
CAPTCHA_FOREGROUND_COLOR = '#991100'

CAPTCHA_FONT_SIZE = 50
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
# CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.word_challenge'
CAPTCHA_WORDS_DICTIONARY = '/usr/share/dict/brazilian'
# end django-simple-captcha config
