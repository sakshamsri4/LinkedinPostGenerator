from datetime import datetime
from typing import Any

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
