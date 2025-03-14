import uuid
import stripe
from app.utils import PaymentProcessingError
from app.schemas.order import PaymentMethod


async def process_payment(amount: float, payment_method: PaymentMethod):
    if payment_method.provider != 'stripe':
        raise PaymentProcessingError("Provedor de pagamento não suportado")
    
    try:
        # Verificar o pagamento no Stripe
        payment_intent = stripe.PaymentIntent.retrieve(
            payment_method.payment_intent_id
        )
        
        if payment_intent.status != 'succeeded':
            raise PaymentProcessingError("Pagamento não autorizado")
            
        return {
            "status": "succeeded",
            "amount": amount,
            "payment_method": payment_method.dict()
        }
        
    except stripe.error.StripeError as e:
        raise PaymentProcessingError(f"Erro Stripe: {str(e)}")