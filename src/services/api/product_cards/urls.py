from dmr.routing import Router, path

from services.api.product_cards.controllers import ProductCardController

router = Router(
    prefix="product-cards/",
    urls=[
        path("", ProductCardController.as_view(), name="generate"),
    ],
)
