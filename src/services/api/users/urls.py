from dmr.routing import Router, path

from services.api.users.controllers import UserMeController

router = Router(
    prefix="users/",
    urls=[path("me/", UserMeController.as_view(), name="me")],
)
