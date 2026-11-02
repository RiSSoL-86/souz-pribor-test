from django.utils.translation import gettext_lazy as _

from django_project.settings import BASE_DIR, env

LANGUAGE_CODE = env("LANGUAGE_CODE")
LANGUAGES = [("en-us", _("English"))]
USE_I18N = True
LOCALE_PATHS = [BASE_DIR / "locale"]
