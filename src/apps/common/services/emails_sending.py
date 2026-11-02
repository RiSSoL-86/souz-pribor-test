from typing import Any, final

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@final
class EmailService:
    """Application-level operations for sending templated emails."""

    @staticmethod
    def send(
        template_name: str,
        recipients: str | list[str],
        context: dict[str, Any] | None = None,
        from_email: str | None = None,
    ) -> None:
        """Render the ``emails/{template_name}`` templates and send them."""
        if isinstance(recipients, str):
            recipients = [recipients]
        if context is None:
            context = {}

        extended_context = {
            **context,
            "site_url": settings.SITE_URL,  # type: ignore[misc]
            "project_name": settings.PROJECT_NAME,
        }
        template_pref = f"emails/{template_name}"

        subject = render_to_string(
            f"{template_pref}/subject.txt", context=extended_context
        ).strip()
        text_content = render_to_string(
            f"{template_pref}/body.txt", context=extended_context
        )
        html_content = render_to_string(
            f"{template_pref}/body.html", context=extended_context
        )

        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipients,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


def send_email(
    template_name: str,
    recipients: str | list[str],
    context: dict[str, Any] | None = None,
    from_email: str | None = None,
) -> None:
    """Send a templated email using the service-level implementation."""
    EmailService.send(template_name, recipients, context, from_email)
