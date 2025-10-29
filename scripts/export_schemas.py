import json
from pydantic.schema import schema as pydantic_schema
from common.schemas.events import UserInputEvent, AgentOutputEvent
from common.schemas.tools import AddToCartRequest, AddToCartResponse

models = [UserInputEvent, AgentOutputEvent, AddToCartRequest, AddToCartResponse]
s = pydantic_schema(models, title="AI Shopping Platform Schemas")
print(json.dumps(s, indent=2))
