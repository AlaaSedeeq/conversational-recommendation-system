from pydantic import BaseModel, Field
from typing import Dict, Any, List

class SearchEngineResponse(BaseModel):
    status: bool
    response: List    # [SearchResult]

    class Config:
        arbitrary_types_allowed = True