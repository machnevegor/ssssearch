from __future__ import annotations

from datetime import datetime
from typing import Optional

import pydantic

__all__ = ("PageMeta",)


class PageMeta(pydantic.BaseModel):
    url: pydantic.HttpUrl
    """URL of the page."""
    sha: Optional[str]
    """SHA-256 hash of the page content if page exists; None otherwise."""
    exp: datetime
    """Expiry date."""
    iat: datetime
    """Creation date."""

    def serialize(self) -> str:
        """Generates a JSON representation of the model."""
        return self.model_dump_json()

    @classmethod
    def parse(cls, raw: str) -> PageMeta:
        """Validate the given JSON data against the model."""
        return cls.model_validate_json(raw)
