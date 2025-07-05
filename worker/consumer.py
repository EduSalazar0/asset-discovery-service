import json
import logging
import sys
from kafka import KafkaConsumer
from sqlalchemy.orm import Session
from pydantic import ValidationError

from core.config import settings
from domain.entities.scan_event import ScanEvent
from application.use_cases.discover_assets import DiscoverAssetsUseCase
from infrastructure.database.connection import SessionLocal
from infrastructure.repositories.postgres_asset_repository import PostgresAssetRepository
from infrastructure.messaging.kafka_producer import KafkaMessagingProducer
from infrastructure.tools.subdomain_finder import SubdomainFinder

# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AssetDiscoveryConsumer:
    def __init__(self):
        try:
            self.consumer = KafkaConsumer(
                settings.KAFKA_SOURCE_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_CONSUMER_GROUP,
                auto_offset_reset='earliest', # Start reading at the earliest message
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            logger.info("Kafka consumer connected successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            sys.exit(1) # Exit if we can't connect to Kafka

    def run(self):
        logger.info(f"Worker started. Listening for messages on topic '{settings.KAFKA_SOURCE_TOPIC}'...")
        
        for message in self.consumer:
            logger.info(f"Received message: {message.value}")
            
            try:
                scan_event = ScanEvent(**message.value)
            except ValidationError as e:
                logger.error(f"Invalid message format: {e}. Skipping message.")
                continue

            # We create a new DB session for each message to ensure session safety.
            db_session: Session = SessionLocal()
            try:
                # Dependency Injection for the use case
                asset_repo = PostgresAssetRepository(db_session)
                producer = KafkaMessagingProducer()
                finder = SubdomainFinder()
                use_case = DiscoverAssetsUseCase(asset_repo, producer, finder)
                
                # Execute the main logic
                use_case.execute(scan_event)
                
                logger.info(f"Successfully processed message for scan_id: {scan_event.scan_id}")
            except Exception as e:
                logger.error(f"An error occurred while processing scan_id {scan_event.scan_id}: {e}", exc_info=True)
                # In production, you might want to send this to a dead-letter queue
            finally:
                db_session.close()

def start_worker():
    worker = AssetDiscoveryConsumer()
    worker.run()