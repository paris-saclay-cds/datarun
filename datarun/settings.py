"""
Django settings for datarun project.

Generated by 'django-admin startproject' using Django 1.9.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

from __future__ import absolute_import
import os
from celery.schedules import crontab


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(i_jfto&x_%z(w#)h_$62y)x+!i745j@dk&xn&4+bl73(h$3-o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'runapp',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger'
]

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

ROOT_URLCONF = 'datarun.urls'

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

WSGI_APPLICATION = 'datarun.wsgi.application'


# REST Framework
# REST_FRAMEWORK = {
#     'DEFAULT_VERSIONING_CLASS':
#     'rest_framework.versioning.AcceptHeaderVersioning',
#     'ALLOWED_VERSIONS': ('0.0'),
#     'DEFAULT_VERSION': '0.0',
# }

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DR_DATABASE_NAME'),
        'USER': os.environ.get('DR_DATABASE_USER'),
        'PASSWORD': os.environ.get('DR_DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

# API documentation django-rest-swagger
# http://django-rest-swagger.readthedocs.org/en/latest/index.html
SWAGGER_SETTINGS = {
    'exclude_namespaces': [],
    'api_version': '0.1',
    'api_path': '/',
    'enabled_methods': [
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    'api_key': '',
    'is_authenticated': True,
    'is_superuser': False,
    'unauthenticated_user': 'django.contrib.auth.models.AnonymousUser',
    'permission_denied_handler': None,
    'resource_access_handler': None,
    # 'base_path':'helloreverb.com/docs',
    'info': {
        'contact': 'camille.marini@telecom-paristech.fr',
        'description': 'Datarun is a rest api that train and test models \
                        on CV fold',
        # 'license': '????',
        # 'licenseUrl': 'http://www.apache.org/licenses/LICENSE-2.0.html',
        'title': 'Datarun',
    },
    'doc_expansion': 'none',
}

# Celery settings
# BROKER_URL = 'amqp://'  # 'amqp://guest:guest@localhost//'
BROKER_URL = 'amqp://%s:%s@%s/%s' % (os.environ.get('DR_DATABASE_USER'),
                                     os.environ.get('DR_DATABASE_PASSWORD'),
                                     os.environ.get('IP_MASTER'),
                                     os.environ.get('RMQ_VHOST'))
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'amqp'
CELERY_RESULT_PERSISTENT = True

TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
CELERYBEAT_SCHEDULE = {
    'save-train-model-in-db': {
        'task': 'runapp.tasks.task_save_submission_fold_db',
        'schedule': crontab(minute=os.environ.get('CELERY_SCHEDULER_PERIOD',
                                                  '*/15')),
        'options': {'queue': 'master_periodic'},
#        'queue': 'master_periodic',
    },
}
