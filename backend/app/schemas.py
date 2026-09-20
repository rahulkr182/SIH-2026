from pydantic import BaseModel
from typing import Optional

class TaskRequest(BaseModel):
    modality: str
    prompt: str
    file_name: Optional[str] = None
    
class TaskResponse(BaseModel):
    status: str
    pipeline_route: str
    message: str
