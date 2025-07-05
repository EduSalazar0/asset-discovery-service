from sqlalchemy.orm import Session

from domain.entities.asset import Asset
from domain.repositories.asset_repository import IAssetRepository
from infrastructure.database.models import AssetDB

class PostgresAssetRepository(IAssetRepository):
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def save(self, asset: Asset) -> Asset:
        asset_db = AssetDB(
            id=asset.id,
            scan_id=asset.scan_id,
            asset_type=asset.asset_type,
            value=asset.value,
            discovered_at=asset.discovered_at
        )
        self.db.add(asset_db)
        self.db.commit()
        self.db.refresh(asset_db)
        return Asset.from_orm(asset_db)