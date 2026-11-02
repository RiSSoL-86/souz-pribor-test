from django.urls import include
from dmr.routing import Router, path

from services.api.auth import urls as auth_urls
from services.api.product_cards import urls as product_cards_urls
from services.api.users import urls as users_urls

router = Router(
    prefix="",
    urls=[
        path(
            auth_urls.router.prefix,
            include(
                (auth_urls.router.urls, "auth"),
                namespace="auth",
            ),
        ),
        path(
            product_cards_urls.router.prefix,
            include(
                (product_cards_urls.router.urls, "product_cards"),
                namespace="product_cards",
            ),
        ),
        path(
            users_urls.router.prefix,
            include(
                (users_urls.router.urls, "users"),
                namespace="users",
            ),
        ),
    ],
)
