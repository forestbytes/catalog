from pydantic import BaseModel
from typing import List, Optional
from rich import print as rprint

class USFSDocument(BaseModel):
    id: str
    title: str
    description: str
    keywords: Optional[List[str]] = None
    src: Optional[str] = None
