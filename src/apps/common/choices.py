from typing import final

from django.db import models
from django.utils.translation import gettext_lazy as _


@final
class Language(models.IntegerChoices):
    """List supported interface languages."""

    RUSSIAN = 0, _("russian")
    ENGLISH = 1, _("english")
