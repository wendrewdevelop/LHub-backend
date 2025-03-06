import uuid
from sqlalchemy import (
    Column, 
    Float, 
    String,
    Boolean,
    JSON
)
from sqlalchemy.dialects.postgresql import UUID
from app.core import Base


class ShippingRuleModel(Base):
    __tablename__ = "tb_shipping_rules"
    
    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name = Column(String(100)) 
    service_code = Column(String(50))
    max_weight = Column(Float) 
    min_dimension = Column(Float) 
    max_dimension = Column(Float) 
    formula = Column(String(255)) 
    origin_cep_ranges = Column(JSON) 
    is_active = Column(Boolean, default=True)
