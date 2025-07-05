from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_CONSUMER_GROUP: str = "asset-discovery-group"
    KAFKA_SOURCE_TOPIC: str = "scan.started"
    KAFKA_DESTINATION_TOPIC: str = "asset.discovered"
    SHODAN_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()