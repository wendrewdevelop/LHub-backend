import os
import stripe
from stripe import StripeClient
from decouple import config


STRIPE_API_SECRET_KEY = config("STRIPE_SECRET_KEY_PROD") if config("ENV") == "PROD" else config("STRIPE_SECRET_KEY_DEV")
stripe.api_key = STRIPE_API_SECRET_KEY
print("Stripe API Key:", stripe.api_key)


async def handle_successful_payment(payment_intent):
    # Lógica de negócio (ex: atualizar banco de dados)
    print(f"Pagamento {payment_intent.id} confirmado!")
    print(f"Valor: {payment_intent.amount / 100} {payment_intent.currency.upper()}")