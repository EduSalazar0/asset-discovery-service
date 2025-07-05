"""Asset entity definition."""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field

from domain.enums.asset_type import AssetType


class Asset(BaseModel):
    """Represents a discovered digital asset."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    scan_id: uuid.UUID
    asset_type: AssetType
    value: str  # e.g., "api.example.com" or "192.168.1.1"
    discovered_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
