import uuid
from app.utils import PaymentProcessingError


async def process_payment(amount: float, payment_method: dict):
    # Implementação mockada - integrar com gateway real
    if payment_method.get('type') == 'credit_card':
        return {
            'gateway': 'stripe',
            'charge_id': f'ch_{uuid.uuid4().hex}',
            'amount': amount,
            'status': 'succeeded'
        }
    raise PaymentProcessingError("Método de pagamento inválido")