from typing import final

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from apps.users.models import User


@final
class UserAdmin(DjangoUserAdmin):  # type: ignore[type-arg]
    """Configure user administration."""

    list_display = ("id", "email", "first_name", "last_name", "is_staff")
    list_display_links = list_display
    ordering = ("email",)
    filter_horizontal = ()
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name")},
        ),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser")},
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    search_fields = ("first_name", "last_name", "email")


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
