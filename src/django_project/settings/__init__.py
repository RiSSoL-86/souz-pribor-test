from pathlib import Path

import environ
from split_settings.tools import include as settings_include
from split_settings.tools import optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
ENV_FILE = BASE_DIR / ".env"
if not ENV_FILE.exists():
    ENV_FILE = BASE_DIR / ".env.example"
environ.Env.read_env(ENV_FILE)

ENVIRONMENT = env("ENVIRONMENT")

ENVIRONMENT_LOCAL = "local"
ENVIRONMENT_DEV = "dev"
ENVIRONMENT_STAGE = "stage"
ENVIRONMENT_PROD = "production"
SUPPORTED_ENVIRONMENTS = {
    ENVIRONMENT_LOCAL,
    ENVIRONMENT_DEV,
    ENVIRONMENT_STAGE,
    ENVIRONMENT_PROD,
}

if ENVIRONMENT not in SUPPORTED_ENVIRONMENTS:
    raise ValueError(f"Unsupported environment: ENVIRONMENT={ENVIRONMENT}")

# Values exported by split settings modules and imported by later fragments.
DEBUG: bool
MIDDLEWARE: list[str]
PROJECT_NAME: str
TIME_ZONE: str

settings_include(
    "common.py",
    "installed_apps.py",
    "auth.py",
    "jwt.py",
    "dmr.py",
    "passwords.py",
    "cache.py",
    "database.py",
    "i18n.py",
    "tz.py",
    "storage.py",
    "celery.py",
    "email.py",
    "llm.py",
    "open_ai.py",
    "logging.py",
    "tests.py",
    "sentry.py",
    optional("local_settings.py"),
)
