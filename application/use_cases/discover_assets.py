from typing import List
import logging

from domain.entities.asset import Asset
from domain.entities.scan_event import ScanEvent
from domain.enums.asset_type import AssetType
from domain.repositories.asset_repository import IAssetRepository
from domain.repositories.messaging_producer import IMessagingProducer
from infrastructure.tools.subdomain_finder import SubdomainFinder

logger = logging.getLogger(__name__)

class DiscoverAssetsUseCase:
    def __init__(
        self,
        asset_repository: IAssetRepository,
        messaging_producer: IMessagingProducer,
        subdomain_finder: SubdomainFinder
    ):
        self.asset_repository = asset_repository
        self.messaging_producer = messaging_producer
        self.subdomain_finder = subdomain_finder

    def execute(self, scan_event: ScanEvent) -> None:
        logger.info(f"Executing asset discovery for scan_id: {scan_event.scan_id}")
        
        # 1. Use tools to find assets
        subdomains: List[str] = self.subdomain_finder.find(scan_event.domain_name)

        if not subdomains:
            logger.warning(f"No subdomains found for domain: {scan_event.domain_name}")
            return

        # 2. For each found asset, create entity, save it, and publish event
        for sub_value in subdomains:
            new_asset = Asset(
                scan_id=scan_event.scan_id,
                asset_type=AssetType.SUBDOMAIN,
                value=sub_value
            )
            
            # Persist the asset
            saved_asset = self.asset_repository.save(new_asset)
            logger.info(f"Saved new asset: {saved_asset.id} - {saved_asset.value}")
            
            # Publish the finding
            self.messaging_producer.publish_asset_discovered(saved_asset)

        logger.info(f"Finished asset discovery for scan_id: {scan_event.scan_id}")