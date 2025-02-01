from pydantic import BaseModel

class CompletionRequest(BaseModel):
    category: str
    prompt: str

class CompletionResponse(BaseModel):
    response: str
