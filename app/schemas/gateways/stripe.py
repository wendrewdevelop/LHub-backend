from pydantic import BaseModel


class PaymentRequest(BaseModel):
    amount: int  # Em centavos (ex: R$10.00 = 1000)
    currency: str = "brl"
    description: str = "Pagamento FastAPI"