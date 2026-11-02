from dmr.routing import Router, path

from services.api.auth.controllers import (
    RefreshController,
    SignInController,
    SignUpController,
)

router = Router(
    prefix="auth/",
    urls=[
        path("signup/", SignUpController.as_view(), name="signup"),
        path("signin/", SignInController.as_view(), name="signin"),
        path("refresh/", RefreshController.as_view(), name="refresh"),
    ],
)
