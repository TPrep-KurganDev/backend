from pydantic import BaseModel

class PushUpdate(BaseModel):
    endpoint: str
    push_key: str