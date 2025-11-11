import os
import sys
from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")


DEBUG = True if os.getenv("DEBUG") == "True" else False

ALLOWED_HOSTS = ["ALLOWED_HOSTS", "*"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework_simplejwt",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "django_celery_beat",
    # 'corsheaders',
    "restaurant",
    "users",
]

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# настройки переключенияЯзыковых настроек сайта
USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = 'ru'
LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    'django.middleware.locale.LocaleMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# CORS_ALLOWED_ORIGINS = [
#     '<http://localhost:8000>',  # Замените на адрес вашего фронтенд-сервера
# ]
#
# CSRF_TRUSTED_ORIGINS = [
#     "https://read-and-write.example.com", #  Замените на адрес вашего фронтенд-сервера
#     # и добавьте адрес бэкенд-сервера
# ]

CORS_ALLOW_ALL_ORIGINS = False

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = 'ru'

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # сюда collectstatic будет копировать всё


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

AUTH_USER_MODEL = "users.User"  # ← указываем, что User — из приложения users

LOGIN_REDIRECT_URL = 'users:profile'
LOGOUT_REDIRECT_URL = 'restaurant:home'
LOGIN_URL = 'users:register'


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"  # Настройки почты
EMAIL_HOST = "smtp.yandex.ru"
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = os.getenv("MAIL_HOST")
EMAIL_HOST_PASSWORD = os.getenv("MAIL_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}

# для теста
# Настройки для тестирования, через SQ-lite включая CI/CD
# if "test" in sys.argv:
#     ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
#
#     # Дополнительные настройки для тестов
#     PASSWORD_HASHERS = [
#         "django.contrib.auth.hashers.MD5PasswordHasher",  # Быстрее для тестов
#     ]
#
#     # 🗃 База данных - для тестов стоковая
#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.sqlite3",
#             "NAME": BASE_DIR / "db.sqlite3",
#         }
#     }
#
#     LANGUAGE_CODE = "ru-ru"
#     TIME_ZONE = "UTC"
#     USE_I18N = True
#     USE_TZ = True
#
#     # 📦 Статика
#     STATIC_URL = "/static/"
#     STATICFILES_DIRS = []
#
#     # 📧 Email
#     EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
#
#     # ПРОИЗВОЛЬНЫЙ КЛЮЧ ДЛЯ ТЕСТОВ
#     SECRET_KEY = "ci-test-secret-key-unsafe-but-ok"
#     DEBUG = True
#     ROOT_URLCONF = "config.urls"
#
#     # 🔑 Указываем, что кастомная модель User — основная
#     AUTH_USER_MODEL = "users.User"
#
#     # 🖼 TEMPLATES — обязательно для админки
#     TEMPLATES = [
#         {
#             "BACKEND": "django.template.backends.django.DjangoTemplates",
#             "DIRS": [],
#             "APP_DIRS": True,
#             "OPTIONS": {
#                 "context_processors": [
#                     "django.template.context_processors.debug",
#                     "django.template.context_processors.request",
#                     "django.contrib.auth.context_processors.auth",
#                     "django.contrib.messages.context_processors.messages",
#                 ],
#             },
#         },
#     ]


# Настройки Celery
if "test" in sys.argv:
    # Настройки для тестов
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    # Используем memory backend вместо Redis
    CELERY_RESULT_BACKEND = "cache"
    CELERY_CACHE_BACKEND = "memory"
else:
    # Реальные настройки
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"


# Используем eventlet на Windows
CELERY_WORKER_POOL = "eventlet"
CELERY_WORKER_POOL_RESTARTS = True

# Опционально: сериализация
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Moscow"

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Настройки Celery Beat (планировщик)
CELERY_BEAT_SCHEDULE = {
    "check-habits-daily": {
        "task": "tracker.tasks.check_all_habits",
        "schedule": crontab(minute=0, hour="*/6"),
    },
}

TELEGRAM_URL = "https://api.telegram.org/bot"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

