import json
import logging
from kafka import KafkaProducer

from core.config import settings
from domain.entities.asset import Asset
from domain.repositories.messaging_producer import IMessagingProducer

logger = logging.getLogger(__name__)

class KafkaMessagingProducer(IMessagingProducer):
    def __init__(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
            )
            logger.info("Kafka producer connected successfully.")
        except Exception as e:
            logger.error(f"Failed to connect Kafka producer: {e}")
            self.producer = None

    def publish_asset_discovered(self, asset: Asset) -> None:
        if not self.producer:
            logger.error("Kafka producer is not available.")
            return

        message = {
            "asset_id": str(asset.id),
            "scan_id": str(asset.scan_id),
            "asset_type": asset.asset_type.value,
            "value": asset.value,
            "discovered_at": asset.discovered_at.isoformat()
        }
        
        try:
            self.producer.send(settings.KAFKA_DESTINATION_TOPIC, value=message)
            self.producer.flush()
            logger.info(f"Published 'asset.discovered' event for asset_id: {asset.id}")
        except Exception as e:
            logger.error(f"Failed to publish message for asset_id {asset.id}: {e}")