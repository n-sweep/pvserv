from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-%li@l%au+qx^wy3)ig7lw&+n-+r-s8#1w#@7e8qr+l^epc^qoe"

DEBUG = True

APPEND_SLASH = False

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "plotviewer.apps.PlotviewerConfig",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path("/data/db.sqlite3"),
    }
}

TIME_ZONE = "UTC"
USE_TZ = True

STATIC_URL = "static/"

DATA_UPLOAD_MAX_MEMORY_SIZE = None
