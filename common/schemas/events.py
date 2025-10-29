from pydantic import BaseModel, Field
from typing import List, Optional, Any

class BaseEnvelope(BaseModel):
    schema_version: str = "1.0"
    correlation_id: str
    causation_id: Optional[str] = None

class UserInputEvent(BaseEnvelope):
    user_id: str
    session_id: str
    text: Optional[str] = None
    structured_intent: Optional[dict] = None
    timestamp: float

class Fragment(BaseModel):
    type: str
    content: Any

class AgentOutputEvent(BaseEnvelope):
    session_id: str
    fragments: List[Fragment]

