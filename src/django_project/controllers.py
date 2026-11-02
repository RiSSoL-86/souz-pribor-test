from typing import TYPE_CHECKING, final, override

from dmr.openapi.views import OpenAPIJsonView

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


@final
class OpenAPIJsonDownloadController(OpenAPIJsonView):
    """Return the OpenAPI schema as a downloadable JSON file."""

    @override
    def get(self, request: HttpRequest) -> HttpResponse:
        """Build the schema response with an attachment header."""

        response = super().get(request)
        response["Content-Disposition"] = 'attachment; filename="schema.json"'
        return response
