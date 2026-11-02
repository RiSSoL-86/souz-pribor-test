from django_project.settings import (
    BASE_DIR,
    ENVIRONMENT,
    ENVIRONMENT_LOCAL,
    env,
)

DEBUG = env.bool("DEBUG")

if DEBUG and ENVIRONMENT != ENVIRONMENT_LOCAL:
    raise ValueError("DEBUG mode is allowed only in the local environment")

SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = [
    origin for origin in env.list("CSRF_TRUSTED_ORIGINS", default=[]) if origin
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ROOT_URLCONF = "django_project.urls"
ASGI_APPLICATION = "django_project.asgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

FORCE_SCRIPT_NAME = env("SCRIPT_NAME", default="") or None
if FORCE_SCRIPT_NAME:
    SESSION_COOKIE_PATH = f"{FORCE_SCRIPT_NAME}/"

SILENCED_SYSTEM_CHECKS = ["auth.E003"]

SITE_URL = env("SITE_URL")
PROJECT_NAME = env("PROJECT_NAME")
