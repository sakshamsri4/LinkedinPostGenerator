from datetime import datetime
from typing import Any
from enum import StrEnum
from pydantic import Field
from pydantic import BaseModel, ConfigDict


class RawItem(BaseModel):
    """What a source returns. No derived fields, no DB identity."""

    model_config = ConfigDict(frozen=True)

    source: str
    external_id: str
    url: str
    title: str
    body: str | None = None
    published_at: datetime | None = None
    payload: dict[str, Any]


class Item(BaseModel):
    """What we store in the DB. Derived fields, DB identity."""

    model_config = ConfigDict(frozen=True)

    id: int | None = None
    source: str
    external_id: str
    url: str
    url_canonical: str
    title: str
    body: str | None
    published_at: datetime | None
    fetched_at: datetime
    raw: str
    
class SourceError(BaseModel):
    """A source that failed. Accumlated in state, never raised."""
    
    model_config= ConfigDict(frozen=True)
    source:str
    message:str
    occurred_at:datetime
    
class Cluster(BaseModel):
    """Items across sources covering one story."""
    
    model_config= ConfigDict(frozen=True)
    
    id:int | None = None
    item_ids:tuple[int,...]
    source_count: int =Field(ge=1)
    created_at:datetime
    
class SeedStatus(StrEnum):
    NEW = "new"
    REJECTED = "rejected"
    DRAFTED = "drafted"
    POSTED = "posted"
    
class Seed(BaseModel):
    """A scored, ranked cluster."""
    
    model_config = ConfigDict(frozen=True)
    
    id: int | None = None
    cluster_id: int
    run_id: str
    topical_fit: float = Field(ge=0.0, le= 1.0)
    novelty: float = Field(ge=0.0, le= 1.0)
    corroboration: float = Field(ge=0.0, le= 1.0)
    score: float = Field(ge=0.0, le= 1.0)
    rank: int | None = None
    status: SeedStatus = SeedStatus.NEW
    created_at: datetime
