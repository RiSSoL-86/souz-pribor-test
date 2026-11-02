import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger

from django_project.settings import ENVIRONMENT, env

if sentry_dsn := env("SENTRY_DSN", default=""):
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        auto_session_tracking=env.bool("SENTRY_AUTO_SESSION_TRACKING"),
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE"),
        environment=ENVIRONMENT,
    )
    ignore_logger("django.security.DisallowedHost")
