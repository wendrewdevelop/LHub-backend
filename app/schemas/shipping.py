from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID


class ShippingCalculateRequest(BaseModel):
    origin_cep: str
    destination_cep: str
    weight: float  # kg
    length: float  # cm
    height: float  # cm
    width: float  # cm

    @field_validator('origin_cep', 'destination_cep')
    def validate_cep(cls, v):
        v = v.replace("-", "").strip()
        if len(v) != 8 or not v.isdigit():
            raise ValueError("CEP inválido")
        return v

class ShippingOptionResponse(BaseModel):
    carrier: str
    service: str
    cost: float
    delivery_time: int  
    description: Optional[str] = None


class LocalDeliveryRequest(BaseModel):
    store_id: UUID
    destination_cep: str
    destination_address: str  # Opcional para cálculo por endereço exato

class LocalDeliveryResponse(BaseModel):
    is_local: bool
    delivery_fee: float
    estimated_time: str  # Ex: "30-45 minutos"
    distance_km: Optional[float] = None