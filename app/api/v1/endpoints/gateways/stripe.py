import os
import stripe
from fastapi import (
    HTTPException, 
    APIRouter, 
    Request, 
    Header
)
from fastapi.responses import JSONResponse
from decouple import config
from app.schemas import StripePaymentRequest
from app.services import handle_successful_payment, stripe_client


router = APIRouter(
    prefix="/gateways/stripe",
    tags=["stripe"],
    responses={
        404: {
            "description": "Not found"
        }
    },
)

@router.post("/payment/intent")
def create_payment_intent(request: StripePaymentRequest):
    try:
        intent = stripe_client.PaymentIntent.create(
            amount=request.amount,
            currency=request.currency,
            description=request.description,
            automatic_payment_methods={"enabled": True}
        )
        return JSONResponse(
            content={
                "intent_id": intent.id,
                "client_secret": intent.client_secret
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/payment/confirm")
def confirm_payment(payment_intent_id: str):
    try:
        # Verifica se é um ID válido (começa com 'pi_')
        if not payment_intent_id.startswith("pi_"):
            raise HTTPException(
                status_code=400,
                detail="ID do PaymentIntent inválido"
            )

        # Recupera o PaymentIntent usando o ID correto
        intent = stripe_client.payment_intents.retrieve(
            payment_intent_id
        )
        
        return {
            "status": intent.status,
            "amount": intent.amount,
            "currency": intent.currency
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro no Stripe: {e}"
        )
    

@router.post("/webhook/payment/intent")
async def handle_webhook(
    request: Request,
    stripe_signature: str = Header(..., alias="Stripe-Signature")  # Nome exato do header
):
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(  # Use o módulo stripe
            payload,
            stripe_signature,
            config("STRIPE_WEBHOOK_DEV")
        )
        print(f"Evento recebido: {event.type}")
        
        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            print(f"💸 Pagamento confirmado: {payment_intent.id}")
            await handle_successful_payment(payment_intent)
        
        return {"status": "success"}
    
    except Exception as e:
        print(f"Erro no webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
