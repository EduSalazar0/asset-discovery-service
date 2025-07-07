import json
import logging
import sys  # <-- Importado para sys.exit
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

# --- Configuración de Logging ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AssetDiscoveryConsumer:
    """
    Una clase que encapsula el consumidor de Kafka.
    Escucha eventos 'scan.requested' e inicia el proceso de descubrimiento de activos.
    """
    logger.info("Configurando KafkaConsumer con request_timeout_ms=30000 y session_timeout_ms=10000")
    def __init__(self):
        """
        Inicializa la conexión con el broker de Kafka.
        Si la conexión falla, es un error crítico y el servicio no puede arrancar.
        Este enfoque "fail-fast" permite que Kubernetes gestione los reinicios.
        """
        try:
            self.consumer = KafkaConsumer(
                settings.KAFKA_SOURCE_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_CONSUMER_GROUP,
                auto_offset_reset='earliest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                session_timeout_ms=10000,
                request_timeout_ms=30000 # Asegura compatibilidad
            )
            logger.info("Kafka consumer conectado exitosamente.")
        except Exception as e:
            # Si no se puede conectar a Kafka al inicio, el worker no puede funcionar.
            # Se registra el error y se termina el proceso. Kubernetes lo reiniciará.
            logger.error(f"Error Crítico: No se pudo conectar a Kafka. Terminando el servicio. Error: {e}")
            sys.exit(1)

    def run(self):
        """
        Inicia el bucle infinito para consumir mensajes.
        Este método es el corazón del worker.
        """
        logger.info(f"Worker iniciado. Escuchando mensajes en el topic '{settings.KAFKA_SOURCE_TOPIC}'...")
        
        for message in self.consumer:
            logger.info(f"Mensaje recibido: {message.value}")
            
            # 1. Validar y Deserializar el Mensaje
            try:
                scan_event = ScanEvent(**message.value)
            except ValidationError as e:
                logger.error(f"Formato de mensaje inválido: {e}. Saltando mensaje.")
                continue

            # 2. Manejar Sesión de Base de Datos y Dependencias por Mensaje
            db_session: Session = SessionLocal()
            try:
                # 3. Inyección de Dependencias
                asset_repo = PostgresAssetRepository(db_session)
                producer = KafkaMessagingProducer()
                finder = SubdomainFinder()
                use_case = DiscoverAssetsUseCase(
                    asset_repository=asset_repo, 
                    messaging_producer=producer, 
                    subdomain_finder=finder
                )
                
                # 4. Ejecutar la Lógica de Negocio
                use_case.execute(scan_event)
                
                logger.info(f"Procesamiento exitoso para el scan_id: {scan_event.scan_id}")

            except Exception as e:
                logger.error(
                    f"Ocurrió un error procesando el scan_id {scan_event.scan_id}: {e}", 
                    exc_info=True
                )
                # En producción, aquí podrías enviar el mensaje a una Dead-Letter Queue (DLQ).
            finally:
                # 5. Asegurar que la sesión de BD siempre se cierre
                db_session.close()
                logger.debug("Sesión de base de datos cerrada.")

def start_worker():
    """Función de utilidad para iniciar el consumidor."""
    consumer = AssetDiscoveryConsumer()
    consumer.run()
