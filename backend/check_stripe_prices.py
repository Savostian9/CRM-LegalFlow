import os
import django
from django.conf import settings
import stripe

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

stripe.api_key = settings.STRIPE_SECRET_KEY

prices_to_check = {
    'STARTER_MONTH': 'price_1SVZ1G1dR7VpHP6kCJhfCmuu',
    'PRO_MONTH': 'price_1SVZ1l1dR7VpHP6k68MJ4qn7'
}

print("Checking Stripe Prices...")
for name, price_id in prices_to_check.items():
    try:
        price = stripe.Price.retrieve(price_id)
        amount = price.unit_amount / 100.0
        currency = price.currency.upper()
        product_id = price.product
        product = stripe.Product.retrieve(product_id)
        product_name = product.name
        print(f"{name} ({price_id}): {amount} {currency} - Product: {product_name}")
    except Exception as e:
        print(f"{name} ({price_id}): ERROR - {e}")
