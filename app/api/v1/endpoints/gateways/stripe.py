import os
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
    params = {
        "amount": request.amount,  # Em centavos (ex: R$10 = 1000)
        "currency": request.currency,
        "description": request.description,
        "automatic_payment_methods": {"enabled": True}
    }
    try:
        intent = stripe_client.payment_intents.create(
            params=params
        )
        return JSONResponse(
            content={
                "intent_id": intent.id
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
