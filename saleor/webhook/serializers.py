from typing import TYPE_CHECKING, List

from django.db.models import Prefetch

from ..product.models import ProductVariantChannelListing

if TYPE_CHECKING:
    # pylint: disable=unused-import
    from ..checkout.models import Checkout


def serialize_checkout_lines(checkout: "Checkout") -> List[dict]:
    data = []
    channel = checkout.channel
    prefetch = Prefetch(
        "variant__channel_listings",
        queryset=ProductVariantChannelListing.objects.filter(channel_id=channel.id),
        to_attr="listings",
    )
    for line in checkout.lines.select_related("variant__product").prefetch_related(prefetch).all():
        variant = line.variant

        if not variant.listings:
            continue

        channel_listing = variant.listings[0]
        product = variant.product
        base_price = variant.get_price(product, [], channel, channel_listing)
        data.append(
            {
                "sku": variant.sku,
                "quantity": line.quantity,
                "base_price": str(base_price.amount),
                "currency": channel.currency_code,
                "full_name": variant.display_product(),
                "product_name": product.name,
                "variant_name": variant.name,
            }
        )
    return data
