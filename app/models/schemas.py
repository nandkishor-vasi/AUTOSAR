from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional

class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    mode: str
    retrieved: List[Dict[str, Any]]

class CompareRequest(BaseModel):
    old_document: str
    new_document: str

class ImpactRequest(BaseModel):
    entity_name: str = Field(min_length=1)
    entity_type: Optional[str] = None
