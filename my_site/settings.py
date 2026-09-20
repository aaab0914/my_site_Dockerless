from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-esgyg9h0dut!3$t%g0#b#-@s@b&1&-h$83d0#^1sl1@i6ldx3q",
)

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1,testserver", cast=Csv())


SITE_ID = 1

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django_extensions",
    "rest_framework",
    "django_filters",
    "rest_framework.authtoken",
    "blog.apps.BlogConfig",
    "images.apps.ImagesConfig",
    "users.apps.UsersConfig",
    "taggit",
    "markdownx",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "my_site.middleware.LoginRequiredMiddleware",
]

ROOT_URLCONF = "my_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "my_site.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",  # Points to the static folder in the project root
]


LOGS_DIR = BASE_DIR / "logs"
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir(parents=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "access.log",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        },
        "django.server": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

LOGIN_URL = "/users/login/"
