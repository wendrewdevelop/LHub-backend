from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    RECEBIDO = "RECEBIDO"
    EM_PREPARO = "EM_PREPARO"
    ENVIADO = "ENVIADO"
    ENTREGUE = "ENTREGUE"
    CANCELADO = "CANCELADO"

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: str | None = None

class OrderStatusResponse(BaseModel):
    current_status: OrderStatus
    last_update: datetime
    history: list[dict]  # Ex: [{"status": "ENVIADO", "timestamp": "...", "notes": "..."}]