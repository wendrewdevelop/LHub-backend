import requests
import stripe
from datetime import datetime


# Configuração
WEBHOOK_SECRET = "whsec_2be9b137c4004fc3df1e865901fd043dd27a86ca78e37ab394ad114d143b188a"  # Mesmo do .env
ENDPOINT_URL = "http://localhost:8000/gateways/stripe/webhook/payment/intent"

# 1. Crie um Payment Intent de teste
stripe.api_key = "sk_test_..."
payment_intent = stripe.PaymentIntent.create(
    amount=1000,
    currency="brl",
    payment_method_types=["card"]
)

# 2. Simule evento
event = stripe.Event.construct_from({
    "id": "evt_test_123",
    "type": "payment_intent.succeeded",
    "data": {
        "object": payment_intent
    },
    "created": int(datetime.now().timestamp())
}, stripe.api_key)

# 3. Gere assinatura
timestamp = datetime.now().timestamp()
payload = f"{timestamp}.{event.to_json()}"
signature = stripe.WebhookSignature._compute_signature(
    payload,
    WEBHOOK_SECRET
)

# 4. Envie para o webhook
headers = {
    "Stripe-Signature": f"t={timestamp},v1={signature}"
}

response = requests.post(
    ENDPOINT_URL,
    json=event.to_dict(),
    headers=headers
)

print("Status Code:", response.status_code)
print("Response:", response.json())