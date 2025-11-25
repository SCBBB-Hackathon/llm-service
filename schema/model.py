from pydantic import BaseModel

## Request 
class LLMRequest(BaseModel):
    prompt: str 
    lora: str 

class LLMChatRequest(BaseModel):
    chat_id: str 
    place: str 
    prompt: str  

class EtiquetteRequest(BaseModel):
    prompt: str
    place: str

class EtiquetteChoiceRequest(BaseModel):
    prompt: str


## Response
class LLMResponse(BaseModel):
    success: bool
    text: str = None
    status_code: int
    error_msg: str = None


