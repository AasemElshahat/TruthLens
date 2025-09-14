"""Simple search result model."""

from typing import Optional
from pydantic import BaseModel


class SearchResult(BaseModel):
    """Simple search result."""
    
    url: str
    title: Optional[str] = None
    content: str