import uuid
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from infrastructure.database.connection import Base
from domain.enums.asset_type import AssetType

class AssetDB(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    asset_type = Column(Enum(AssetType), nullable=False)
    value = Column(String, nullable=False)
    discovered_at = Column(DateTime, nullable=False)