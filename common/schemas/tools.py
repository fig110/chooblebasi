from pydantic import BaseModel, Field
from typing import Optional

class ToolBase(BaseModel):
    schema_version: str = "1.0"
    correlation_id: str
    idempotency_key: str

class AddToCartRequest(ToolBase):
    user_id: str
    cart_id: str
    product_id: str
    quantity: int = 1

class AddToCartResponse(BaseModel):
    schema_version: str = "1.0"
    correlation_id: str
    cart_id: str
    line_id: str
    status: str
    message: Optional[str] = None
